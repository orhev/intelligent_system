from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense
import pandas as pd
from os import path


def create_score_route_model(size_input, model_path):
    """
    Create an initial model for road grading

     Parameters
    ----------
    features : List
        The features for evaluating the route score
    model_path : String
        keras model's path

    """

    # train the model
    if path.exists(model_path):
        model = load_model(model_path)
    else:
        model = Sequential()
        model.add(Dense(50, activation='relu', kernel_initializer='ones', bias_initializer='zeros',
                        input_dim=size_input))
        model.add(Dense(25, activation='relu', kernel_initializer='ones', bias_initializer='zeros'))
        model.add(Dense(1, activation='relu', kernel_initializer='ones', bias_initializer='zeros'))

        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

        # save model
        model.save(model_path)
    return model


def predict_new_route_score(route, model_path):
    """
    Get prediction for new route score

    Parameters
    --------------------
    route :List
        New route properties
        The parameters for evaluating the route score will give in the following order:
        ['length', 'travel time', 'bus exchange', 'number of stops',  'average incline', 'maximum incline',
         'sharp incline percent', 'sharp incline distance']
    model_path : String
        keras model's path

    Returns
    -------------
    new_route_score = Float
        new route rating estimate
    """
    model = load_model(model_path)
    new_route_score = model.predict([route])
    return new_route_score


def update_model(model_path, new_routes_array):
    """
    Train model based on new data
    Parameters
    -------------------
    model_path : String
        keras model's path
    new_routes_array : two-dimensional numpy array
        Array of routes properties
        The rows symbolize different routes and the columns symbolize different properties.
        The parameters for evaluating the route score will give in the following order:
        ['length (km)', 'travel time', 'bus exchange', 'number of stops',  'average incline', 'maximum incline',
         'sharp incline percent', 'sharp incline distance(meter)', 'score']
    """
    columns_name = ['length', 'travel time', 'bus exchange', 'number of stops', 'average incline', 'maximum incline',
                    'sharp incline percent', 'sharp incline distance', 'score']
    df = pd.DataFrame(new_routes_array, columns=columns_name)

    # Scale the data so that all parameters are in same scaling range [0,1]
    max_value = {'length': 10, 'travel time': 180, 'bus exchange': 1, 'number of stops': 50, 'average incline': 100,
                 'maximum incline': 100,  'sharp incline percent': 100, 'sharp incline distance': 10000,
                 'score': 5}
    for col in df:
        df[col] = df[col] / max_value[col]

    X_new = df[['length', 'travel time', 'bus exchange', 'number of stops',  'average incline', 'maximum incline',
                'sharp incline percent', 'sharp incline distance']]
    y_new = df[['score']]

    # load model
    model = load_model(model_path)
    # fit the model on new data
    model.fit(X_new, y_new, epochs=100, batch_size=32, verbose=0)

    # save updated model
    model.save(model_path)
