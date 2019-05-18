import time
from pprint import pprint
from tkinter import Tk, filedialog

import pandas as pd
from django.core.management import BaseCommand
import os, sys
import django
from django.db.models import F
import LoadModel as load
import dataprocess as proc
import databaseQueries as dbQuery
from retrainModel import retrain

sys.path.append(r'C:\\Users\j.turnbull\PycharmProjects\SentimentApp')
sys.path.append(r'C:\\Users\j.turnbull\PycharmProjects\SentimentApp\SentimentApp')
sys.path.append(r'C:\Users\j.turnbull\PycharmProjects\SentimentApp') # add path to project root dir
# os.environ["DJANGO_SETTINGS_MODULE"] = "SentimentApp.settings"
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SentimentApp.settings')

# for more sophisticated setups, if you need to change connection settings (e.g. when using django-environ):
#os.environ["DATABASE_URL"] = "postgres://myuser:mypassword@localhost:54324/mydb"

# Connect to Django ORM
django.setup()

# process data
# Review.objects.create(reviewText='MyAgency', predictSentiment='POSITIVE', actualSentiment='POSITIVE')
from tracker.models import Review
from tracker.models import PosScores
from tracker.models import NegScores
from tracker.models import WeightedAvg


# def populate_batch_no():
#     batch_no=None
#
#     if Review.objects.order_by('-batch_no').first() == None:
#         batch_no = 1
#         return batch_no
#
#     last_batch_no = Review.objects.order_by('-batch_no').first().batch_no
#     if last_batch_no == 1:
#         batch_no = last_batch_no + 1
#     # print(last_batch_no)
#     return batch_no
#
# batch_no = populate_batch_no()

def populatePosScores(arr):
    model = PosScores()
    model.precision = arr[0]
    model.recall = arr[1]
    model.f1 = arr[2]
    model.support = arr[3]

    model.save()

    print(PosScores.objects.last().id)
    print("PosScores Dataframe to database COMPLETED")

def populateNegScores(arr):
    model = NegScores()
    model.precision = arr[0]
    model.recall = arr[1]
    model.f1 = arr[2]
    model.support = arr[3]
    model.save()

    print(NegScores.objects.last().id)
    print("NegScores Dataframe to database COMPLETED")


def populateWeightedAvg(arr):
    model = WeightedAvg()
    model.precision = arr[0]
    model.recall = arr[1]
    model.f1 = arr[2]
    model.support = arr[3]
    model.save()

    print(NegScores.objects.last().id)
    print("WeightedAvg Dataframe to database COMPLETED")


# def populateScores(df):
#     for index, row in df.iterrows():
#         model = Scores()
#         model.precision = row['precision']
#         model.recall = row['recall']
#         model.f1 = row['f1']
#         model.support = row['support']
#         model.batch_no = batch_no
#         model.save()
#
#     print(Scores.objects.last().batch_no)
#     print("Dataframe to database COMPLETED")

def populateReviews(view):

    print("Populating database started...")

    # if not view['reviewText'] and not view['reviewText'] and not view['reviewText']:
    if not isinstance(view, pd.DataFrame):
        sys.exit("Incorrect instance, please supply a pandas dataframe with columns:"
                 "reviewText, prediction, sentiment")

    if 'reviewText' in view.columns and 'prediction' in view.columns and 'sentiment' in view.columns:
        df = pd.DataFrame()
        df['reviewstext'] = view['reviewText']
        df['prediction'] = view['prediction']
        df['actual'] = view['sentiment']


        for index, row in df.iterrows():
            model = Review()
            model.reviewText = row['reviewstext']
            model.predictSentiment = row['prediction']
            model.actualSentiment = row['actual']
            model.pos_batch_no = PosScores.objects.last()
            model.neg_batch_no = NegScores.objects.last()
            model.avg_batch_no = WeightedAvg.objects.last()

            model.save()
    else:
        sys.exit("Incorrect Dateframe formatting")

def populateDatabase(path, filesAdded, *args):
    start = time.time() # start time

    df = proc.getDF(path)
    df = proc.addSenimentColumn(df, 'd1')
    view, classificationReport = load.classify(df)

    #populates tables with classification scores
    populatePosScores(classificationReport[0])
    populateNegScores(classificationReport[1])
    populateWeightedAvg(classificationReport[-1])

    #populates the reviews table
    populateReviews(view)

    print("Completed successfully!")

    end = time.time()
    print("Populating databases took:    {} seconds".format(end - start))

    # new data is used to produce a new model
    testDF = pd.read_csv(r'C:\\Users\j.turnbull\PycharmProjects\SentimentApp\Datasets\TestData\TestData.csv')
    model_filename, tfidf_filename = retrain(df, testDF, args)

    filesAdded.append(model_filename)
    filesAdded.append(tfidf_filename)

    return filesAdded

