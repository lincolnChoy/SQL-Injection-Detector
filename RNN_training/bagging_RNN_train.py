import gc
from sklearn import model_selection
from keras.models import Sequential

from keras.layers.embeddings import Embedding
from keras.layers import  Dense,  LSTM
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import numpy as np

from preprocessing import format_query, vectorize_stories, get_word_index

all_data = []
train_data = []
test_data = []
dataset = 'norm'


def trainRNN(vocab_len, max_query_len):
    embedding_size = 32
    model = Sequential()
    model.add(Embedding(vocab_len, embedding_size, input_length=max_query_len))
    model.add(LSTM(200))
    model.add(Dense(1, activation='sigmoid'))

    return model


def bagging(vocab_len, max_query_len):

    num_classifiers = 5

    for i in range(num_classifiers):
        gc.collect()
        kf = model_selection.KFold(n_splits=5,
                                   shuffle=True
                                   )

        #Puts data into array
        for train_index, test_index in kf.split(end_train_x):
            X_train, X_test = end_train_x[train_index], end_train_x[test_index]
            y_train, y_test = end_train_y[train_index], end_train_y[test_index]

        gc.collect()
        y_train = np.uint8(y_train)
        y_test = np.uint8(y_test)
        model = trainRNN(vocab_len, max_query_len)
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

        gc.collect()

        history = model.fit(X_train, y_train, validation_data=(X_test, y_test), batch_size=128, epochs=10)

        filename = 'trained_models/' + dataset + '_bagging_RNN_10_epochs_' + str(i) + '.h5'
        model.save(filename)

        print(history.history.keys())
        # summarize history for accuracy
        plt.figure(figsize=(12, 12))
        plt.plot(history.history['acc'])
        plt.plot(history.history['val_acc'])
        plt.title('model accuracy')
        plt.ylabel('accuracy')
        plt.xlabel('epoch')
        plt.legend(['train', 'test'], loc='upper left')
        plt.show()


with open('datasets/' + dataset + 'Test.txt', 'r') as f:
    for line in f:
        all_data.append(format_query(line))

word_index = get_word_index(dataset + '_vocab.txt')
vocab_len = len(word_index) + 1

# First we will build a set of all the words in the dataset:
train_data, test_data = train_test_split(all_data, test_size = 0.25, random_state = 1)

# Now we are going to calculate the longest query
# We need this for the Keras pad sequences.
all_query_lens = [len(data[0]) for data in all_data]
max_query_len = (max(all_query_lens))

end_train_x, end_train_y = vectorize_stories(train_data, word_index, max_query_len)
end_test_x, end_test_y = vectorize_stories(test_data, word_index, max_query_len)

bagging(vocab_len, max_query_len)
