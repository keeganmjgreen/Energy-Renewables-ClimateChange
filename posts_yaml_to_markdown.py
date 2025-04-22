from argparse import ArgumentParser
from pathlib import Path

from dotenv import load_dotenv

from post_collection import PostCollection

load_dotenv()


def to_markdown_file(
    post_collection: PostCollection, markdown_file: Path | str
) -> None:
    posts = [post for post in post_collection.posts.values() if post.order is not None]
    posts.sort(key=(lambda post: post.order))
    with open(str(Path(markdown_file)), "w") as f:
        f.write("# Posts\n\n")
        f.writelines(post.to_markdown() for post in posts)


parser = ArgumentParser()
parser.add_argument("--yaml-file")
parser.add_argument("--markdown-file")
args = parser.parse_args()
post_collection = PostCollection.from_yaml_file(args.yaml_file)
to_markdown_file(post_collection, args.markdown_file)
