from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from keras.callbacks import EarlyStopping
from keras.utils.np_utils import to_categorical

from sklearn.model_selection import train_test_split

from utils.utils import get_data_and_label

import pandas
import tensorflow as tf
tf.random.set_seed(1)



class Model:
  
  def __init__(self, data: pandas.DataFrame, save_path: str) -> None:
    self.__generate(data, save_path)
    
  def __generate(self, data: pandas.DataFrame, save_path: str) -> None:
    columns = [
      "is_flag", 
      "is_rectangle", 
      "is_trapezoid",
      "is_triangle",
      "plot_aspect_ratio", 
      "plot_interior_angle_sum",
      "plot_obb_ratio", 
    ]
    X_train, X_test, y_train, y_test = train_test_split(  
        data[columns], data["plot_label"], stratify=data["plot_label"], random_state=1, test_size=0.4
    )

    y_train = to_categorical(y_train)
    y_test = to_categorical(y_test) 
    
    model = Sequential()

    model.add(Dense(128, input_shape=(len(columns),), activation='relu'))
    model.add(Dense(32, activation='relu'))
    model.add(Dense(16, activation='relu'))
    model.add(Dense(5, activation='softmax'))

    model.compile(
      loss='categorical_crossentropy', 
      optimizer='Adam', 
      metrics=["accuracy"]
    )

    early_stopping = EarlyStopping(monitor='val_loss', min_delta=0, patience=100, mode='auto')
    model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=1000, callbacks=[early_stopping])
    print(model.evaluate(X_test, y_test))
    model.save(save_path)
    

if __name__ == "__main__":
  Model(data=get_data_and_label(), save_path="model/plot-shape-estimator.pb")