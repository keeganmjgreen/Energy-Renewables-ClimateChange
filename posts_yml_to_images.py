from __future__ import annotations

import dataclasses
import os
from argparse import ArgumentParser
from pathlib import Path
from typing import Any, Dict, List, Union

import yaml
from html2image import Html2Image
from jinja2 import Environment, FileSystemLoader

env = Environment(
    loader=FileSystemLoader("Energy-Renewables-ClimateChange/post_template/")
)
template = env.get_template("template.jinja.html")


TEXT_REPLACEMENT_MAP = {
    "---": "—",
    "--": "–",
    "``": "“",
    "''": "”",
    "`": "‘",
    "'": "’",
    "_2": "<small>2</small>",
}


def replace(s: str) -> str:
    for to_replace, replace_with in TEXT_REPLACEMENT_MAP.items():
        s = s.replace(to_replace, replace_with)
    return s


class PostImage:
    index: int
    title: str
    content: List[str]
    image: str
    image_align_h: int
    image_align_v: int
    image_caption: str
    image_credit: str

    def __init__(
        self,
        title: Union[str, List[str]] = "",
        content: Union[str, List[str]] = "",
        image: str = "",
        image_align_h: int = 0,
        image_align_v: int = 0,
        image_caption: str = "",
        image_credit: str = "",
    ):
        if type(title) is list:
            title = "<br>".join(title)
        title = replace(title)
        self.title = title

        if type(content) is str:
            content = [content]
        for i, c in enumerate(content):
            content[i] = replace(c)
        self.content = "".join([f"<p>{c}</p>" for c in content])

        if image:
            self.image = f"<img src='{image}' style='object-position: {image_align_h}px {image_align_v}px'>"
        else:
            self.image = ""

        self.image_caption = image_caption
        if self.image_caption:
            self.image_caption = f"<em>{self.image_caption}</em>&nbsp;<small>▶</small>"

        self.image_credit = image_credit


class Post:
    index: int
    order: Union[int, None]
    post_image: Union[PostImage, None]
    text: str
    notes: Union[str, List[str]]
    hidden: bool

    def __init__(
        self,
        index: int,
        order: Union[int, None] = None,
        post_image: Union[Dict[str, Any], None] = None,
        text: Union[str, List[str]] = "",
        notes: Union[str, List[str]] = "",
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
        text = replace(text)
        self.text = text

        self.notes = notes
        self.hidden = hidden

    @property
    def post_image_fname(self) -> str:
        return f"{self.index}.png"

    def to_markdown(self) -> str:
        return (
            f"## Post {self.order}\n\n"
            f"{self.text}\n\n"
            f"### {self.post_image.title}\n\n"
            f"{self.post_image.content}\n\n"
        )


@dataclasses.dataclass
class PostCollection:
    posts: Dict[int, Post]

    def from_yaml_file(
        dir: Union[Path, str], fname: str = "posts.yml"
    ) -> PostCollection:
        with open(str(Path(dir, fname))) as f:
            posts = {}
            for index, post_fields in yaml.safe_load(f).items():
                try:
                    posts[index] = Post(index, **post_fields)
                except:
                    print(index, post_fields)
            return PostCollection(posts)

    def to_markdown_file(self, dir: Union[Path, str], fname: str = "posts.md") -> None:
        posts = [post for post in self.posts.values() if post.order is not None]
        posts.sort(key=(lambda post: post.order))
        with open(str(Path(dir, fname)), "w") as f:
            f.write("# Posts\n\n")
            f.writelines(post.to_markdown() for post in posts)

    def posts_to_images(self, post_indices: Union[List[int], None] = None) -> None:
        hti = Html2Image(size=(1200, 1200))

        for post in self.posts.values():
            if post_indices is not None and post.index not in post_indices:
                continue
            if post.hidden:
                continue
            output = template.render(**post.post_image.__dict__)
            hti.screenshot(
                html_str=output,
                css_file="Energy-Renewables-ClimateChange/post_template/styles.css",
                save_as=post.post_image_fname,
            )
            os.system(f"code {post.index}.png")

            print(f"\n{post.text}\n")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--post-indices", default=None)
    parser.add_argument("--to-markdown", action="store_true")
    args = parser.parse_args()
    if args.post_indices is None:
        post_indices = None
    else:
        post_indices = list(map(int, args.post_indices.split(",")))
    post_collection = PostCollection.from_yaml_file(
        dir="Energy-Renewables-ClimateChange/"
    )
    if args.to_markdown:
        post_collection.to_markdown_file(dir="Energy-Renewables-ClimateChange/")
    else:
        post_collection.posts_to_images(post_indices)
