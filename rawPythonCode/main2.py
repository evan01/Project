import tensorflow as tf
import numpy as np
import csv
from tqdm import tqdm
import multiprocessing
import os
import datetime
from os import listdir
from os.path import isfile, join
import re

neuralLock = multiprocessing.Lock()

'''
    PATHS
'''
TRAINING_IMAGES = './data/X_Train'
TESTING_IMAGES = './data/X_Test'
TRAINING_VALS = './data/Y_Train.csv'
LOGGING_PATH = './tensorFlowLog'
MODEL_PATH = './data/CNN_Models/output_graph.pb'
RESULTS_PATH = './data/testResults/output_labels.csv'


def create_CNNetwork():
    with tf.gfile.FastGFile(MODEL_PATH, 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        _ = tf.import_graph_def(graph_def, name='')


def guessImage(imPath):
    """
    When you want to guess just one image
    """
    answer = None
    # start up tensor flow
    create_CNNetwork()
    if not tf.gfile.Exists(imPath):
        tf.logging.fatal("File doesn't exist")
        tf.logging.fatal(imPath)
        exit(1)

    with tf.Session() as sess:
        # aquire the tensor of the CNN we want to check
        softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')
        image_data = tf.gfile.FastGFile(imPath, 'rb').read()
        predictions = sess.run(
            softmax_tensor,
            {'DecodeJpeg/contents:0': image_data}
        )
        guess = np.squeeze(predictions)
        if (guess[0] > guess[1]):
            # Then the net thinks it's a cat
            answer = "Cat"
        else:
            # Then the net thinks it's a dog
            answer = "Dog"
        print('This is a picture of a: ' + answer)
        print("Confidence Cat: " + str(guess[0]))
        print("Confidence Dog: " + str(guess[1]))
        print(" ")


def getTestingLabels():
    # for i in range(1477):
    #     test_labels.append(str(i)+".jpg")
    test_labels = [f for f in os.listdir(TESTING_IMAGES + "/") if f.endswith(".jpg")]
    return test_labels


def main():
    '''
    This program assumes a pre-trained network, created in Bazel
    :return: 
    '''
    # Remove the results file if it already exists
    if isfile(RESULTS_PATH):
        os.remove(RESULTS_PATH)

    # First get all of the paths to testing images, as well as their actual classification
    labels = getTestingLabels()

    # Just when testing..
    labels = labels

    # Create the neural network
    create_CNNetwork()
    results = []

    print("Classifying the photos in" + str(TESTING_IMAGES) + "...")
    with tf.Session() as sess:
        # aquire the tensor of the CNN we want to check
        softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')

        # Then start testing all indv images against the network
        for i in tqdm(labels):
            imName = i
            imPath = TESTING_IMAGES + "/" + imName
            if not tf.gfile.Exists(imPath):
                tf.logging.fatal("File doesn't exist")
                tf.logging.fatal(imPath)
                exit(1)

            image_data = tf.gfile.FastGFile(imPath, 'rb').read()
            predictions = sess.run(
                softmax_tensor,
                {'DecodeJpeg/contents:0': image_data}
            )
            guess = np.squeeze(predictions)
            # Determine what the network predicted
            if (guess[0] > guess[1]):
                # Then the net thinks it's a cat
                answer = 0
            else:
                # Then the net thinks it's a dog
                answer = 1
            results.append((i, str(answer)))
            # Then append the data to the file
    results = sorted(results, key=lambda x: x[0])
    dt = datetime.date.today()
    with open(RESULTS_PATH, 'a') as resultsFile:
        print("---Results File Content---")
        resultsFile.write("Image,Label")
        for i in results:
            print(i[0] + "," + i[1])
            resultsFile.write("\n" + i[0] + "," + i[1])
    resultsFile.close()


main()