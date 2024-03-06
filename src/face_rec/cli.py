from . import dataset_face
from . import face_recognition
from . import model_creation
import click

@click.group()
def cli():
    pass

@cli.command(help="Command for dataset Creation")
@click.option("-i", "--input", help="Input video", default=0, required=False)
@click.option("-w", "--width", help="Input video width", default=640, required=False)
@click.option("-h", "--height", help="Input video height", default=480, required=False)
@click.option("-id", "--identifier", prompt="Enter user id end press <return> ==>", type=int)
def createdataset(input, width, height, identifier):
    dataset_face.main(input, width, height, identifier)

@cli.command(help="Command for dataset Creation")
@click.option("-p", "--path", help="Path to store the dataset", default='dataset', required=False)
@click.option("-m", "--model", help="Path to store the model", default='./trainer1.yml', required=False)
def train(path, model):
    model_creation.main(path, model)

@cli.command(help="Test the face recognition")
@click.option("-i", "--input", help="Input video", default=0, required=False)
@click.option("-m", "--model", help="Path to store the model", default='./trainer.yml', required=False)

def tester(input, model):
    face_recognition.main(input, model)

if __name__ == "__main__":
    cli()
