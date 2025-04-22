from argparse import ArgumentParser

from dotenv import load_dotenv

from post_collection import PostCollection

load_dotenv()


parser = ArgumentParser()
parser.add_argument("--yaml-file")
parser.add_argument("--post-indices", default=None)
args = parser.parse_args()
if args.post_indices is None:
    post_indices = None
else:
    post_indices = list(map(int, args.post_indices.split(",")))
post_collection = PostCollection.from_yaml_file(args.yaml_file)
post_collection.posts_to_images(post_indices)
