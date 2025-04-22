from __future__ import annotations

import dataclasses
import os
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader


TEXT_REPLACEMENT_MAP = {
    "---": "—",
    "--": "–",
    "``": "“",
    "''": "”",
    "`": "‘",
    "'": "’",
    "_2": "<small>2</small>",
}


@dataclasses.dataclass
class PostCollection:
    posts: dict[int, Post]

    def from_yaml_file(yaml_file: Path | str) -> PostCollection:
        with open(str(Path(yaml_file))) as f:
            posts = {}
            for index, post_fields in yaml.safe_load(f).items():
                try:
                    posts[index] = Post(index, **post_fields)
                except Exception:
                    print(index, post_fields)
            return PostCollection(posts)

    def posts_to_images(
        self,
        post_indices: list[int] | None = None,
        size: tuple[int, int] = (1200, 1200),
    ) -> None:
        post_template_path = Path(os.environ["POST_TEMPLATE_PATH"])
        env = Environment(loader=FileSystemLoader(post_template_path.parent))
        post_template = env.get_template(post_template_path.parts[-1])
        for post in self.posts.values():
            if post_indices is not None and post.index not in post_indices:
                continue
            if post.hidden:
                continue
            output = post_template.render(**post.post_image.__dict__)
            Path(f"{post.index}.html").write_text(output)
            chrome_headless_shell_path = os.environ["CHROME_HEADLESS_SHELL_PATH"]
            os.system(
                f"{chrome_headless_shell_path} "
                "--no-sandbox "
                f"--screenshot={post.post_image_fname} "
                f"--window-size={size[0]},{size[1]} "
                "--hide-scrollbars "
                f"{post.index}.html"
            )
            os.system(f"rm {post.index}.html")
            os.system(f"code {post.post_image_fname}")


class Post:
    index: int
    order: int | None
    post_image: PostImage | None
    text: str
    notes: str | list[str]
    hidden: bool

    def __init__(
        self,
        index: int,
        order: int | None = None,
        post_image: dict[str, Any] | None = None,
        text: str | list[str] = "",
        notes: str | list[str] = "",
        hidden: bool = False,
    ):
        self.index = index
        self.order = order

        if post_image is not None:
            self.post_image = PostImage(**post_image)
        else:
            self.post_image = None

        if type(text) is list:
            text = "\n\n".join(text)
        text = _replace(text)
        self.text = text

        self.notes = notes
        self.hidden = hidden

    @property
    def post_image_fname(self) -> str:
        return f"posts/{self.index}.png"

    def to_markdown(self) -> str:
        return (
            f"## Post {self.order}\n\n"
            f"{self.text}\n\n"
            f"### {self.post_image.title}\n\n"
            f"{self.post_image.content}\n\n"
        )


class PostImage:
    index: int
    title: str
    content: list[str]
    image: str
    image_align_h: int
    image_align_v: int
    image_caption: str
    image_credit: str

    def __init__(
        self,
        title: str | list[str] = "",
        content: str | list[str] = "",
        image: str = "",
        image_align_h: int = 0,
        image_align_v: int = 0,
        image_caption: str = "",
        image_credit: str = "",
    ):
        if type(title) is list:
            title = "<br>".join(title)
        title = _replace(title)
        self.title = title

        if type(content) is str:
            content = [content]
        for i, c in enumerate(content):
            content[i] = _replace(c)
        self.content = "".join([f"<p>{c}</p>" for c in content])

        if image:
            self.image = f"<img src='{image}' style='object-position: {image_align_h}px {image_align_v}px'>"
        else:
            self.image = ""

        self.image_caption = image_caption
        if self.image_caption:
            self.image_caption = f"<em>{self.image_caption}</em>&nbsp;<small>▶</small>"

        self.image_credit = image_credit


def _replace(s: str) -> str:
    for to_replace, replace_with in TEXT_REPLACEMENT_MAP.items():
        s = s.replace(to_replace, replace_with)
    return s
