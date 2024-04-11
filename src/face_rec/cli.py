from . import dataset_face
from . import model_creation
from . import test_model
from . import interface
import click

@click.group()
def cli():
    pass

@cli.command(help="Start application")
@click.option("-i", "--input", help="Avatar input", default="./avatar.mp4", required=False)
@click.option("-m", "--model", help="Path of detection model", default='./trainer.yml', required=False)
@click.option("-d", "--image", help="Images container path", default='./Immagini Proverbi', required=False)
@click.option("-f", "--music", help="Music container path", default='./music', required=False)
def create_interface(input, model, image, music):
    interface.main(input, model, image, music)

@cli.command(help="Command for dataset Creation")
@click.option("-i", "--input", help="Input video", default=0, required=False)
@click.option("-w", "--width", help="Input video width", default=640, required=False)
@click.option("-h", "--height", help="Input video height", default=480, required=False)
@click.option("-id", "--identifier", prompt="Enter user id end press <return> ==>", type=int)
def createdataset(input, width, height, identifier):
    dataset_face.main(input, width, height, identifier)

@cli.command(help="Command for Train the detection model")
@click.option("-p", "--path", help="Path to store the dataset", default='dataset', required=False)
@click.option("-m", "--model", help="Path to store the model", default='./trainer.yml', required=False)
def train(path, model):
    model_creation.main(path, model)

@cli.command(help="Command to test the detection on single image")
@click.option("-i", "--input", help="Input image", default="dataset/Validation/User.15.9.png", required=False)
@click.option("-m", "--model", help="Path to store the model", default='./test.yml', required=False)
def testmodel(input, model):
    test_model.main(input, model)

if __name__ == "__main__":
    cli()
