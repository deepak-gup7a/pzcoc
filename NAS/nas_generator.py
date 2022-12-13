import os
import random
import warnings
import pandas as pd
from keras import optimizers
from keras.models import Sequential
from keras.layers import Flatten, Dense, Dropout

from CONSTANTS import *


class NASSearchSpace(object):

    def __init__(self, target_classes):

        self.target_classes = target_classes
        self.vocab = self.vocab_dict()

    def vocab_dict(self):
        nodes = [8, 16, 32, 64, 128, 256, 512]
        act_funcs = ['sigmoid', 'tanh', 'relu', 'elu']
        layer_params = []
        layer_id = []
        for i in range(len(nodes)):
            for j in range(len(act_funcs)):
                layer_params.append((nodes[i], act_funcs[j]))
                layer_id.append(len(act_funcs) * i + j + 1)
        vocab = dict(zip(layer_id, layer_params))
        vocab[len(vocab) + 1] = (('dropout'))
        if self.target_classes == 1:
            vocab[len(vocab) + 1] = (self.target_classes - 1, 'sigmoid')
        else:
            vocab[len(vocab) + 1] = (self.target_classes, 'softmax')
        return vocab

    def encode_sequence(self, sequence):
        keys = list(self.vocab.keys())
        values = list(self.vocab.values())
        encoded_sequence = []
        for value in sequence:
            encoded_sequence.append(keys[values.index(value)])
        return encoded_sequence

    def decode_sequence(self, sequence):
        keys = list(self.vocab.keys())
        values = list(self.vocab.values())
        decoded_sequence = []
        for key in sequence:
            decoded_sequence.append(values[keys.index(key)])
        return decoded_sequence


class NASGenerator(NASSearchSpace):

    def __init__(self):

        self.target_classes = TARGET_CLASSES
        self.nas_optimizer = NAS_OPTIMIZER
        self.nas_lr = NAS_LEARNING_RATE
        self.nas_decay = NAS_DECAY
        self.nas_momentum = NAS_MOMENTUM
        self.nas_dropout = NAS_DROPOUT
        self.nas_loss_func = NAS_LOSS_FUNCTION
        self.nas_one_shot = NAS_ONE_SHOT
        self.metrics = ['accuracy']

        super().__init__(TARGET_CLASSES)


        if self.nas_one_shot:
            self.weights_file = 'LOGS/shared_weights.pkl'
            self.shared_weights = pd.DataFrame({'bigram_id': [], 'weights': []})
            if not os.path.exists(self.weights_file):
                print("Initializing shared weights dictionary...")
                self.shared_weights.to_pickle(self.weights_file)

    def create_model(self, sequence, nas_input_shape):
        layer_configs = self.decode_sequence(sequence)
        model = Sequential()
        if len(nas_input_shape) > 1:
            model.add(Flatten(name='flatten', input_shape=nas_input_shape))
            for i, layer_conf in enumerate(layer_configs):
                if layer_conf is 'dropout':
                    model.add(Dropout(self.nas_dropout, name='dropout'))
                else:
                    model.add(Dense(units=layer_conf[0], activation=layer_conf[1]))
        else:
            for i, layer_conf in enumerate(layer_configs):
                if i == 0:
                    model.add(Dense(units=layer_conf[0], activation=layer_conf[1], input_shape=nas_input_shape))
                elif layer_conf is 'dropout':
                    model.add(Dropout(self.nas_dropout, name='dropout'+str(random.randint(0,10000000000))))
                else:
                    model.add(Dense(units=layer_conf[0], activation=layer_conf[1]))
        return model

    def compile_model(self, model):
        if self.nas_optimizer == 'sgd':
            optim = optimizers.SGD(lr=self.nas_lr, decay=self.nas_decay, momentum=self.nas_momentum)
        else:
            optim = getattr(optimizers, self.nas_optimizer)(lr=self.nas_lr, decay=self.nas_decay)
        model.compile(loss=self.nas_loss_func, optimizer=optim, metrics=self.metrics)
        return model

    def update_weights(self, model):
        layer_configs = ['input']
        for layer in model.layers:
            if 'flatten' in layer.name:
                layer_configs.append(('flatten'))
            elif 'dropout' not in layer.name:
                layer_configs.append((layer.get_config()['units'], layer.get_config()['activation']))
        config_ids = []
        for i in range(1, len(layer_configs)):
            config_ids.append((layer_configs[i - 1], layer_configs[i]))
        j = 0
        for i, layer in enumerate(model.layers):
            if 'dropout' not in layer.name:
                warnings.simplefilter(action='ignore', category=FutureWarning)
                bigram_ids = self.shared_weights['bigram_id'].values
                search_index = []
                for i in range(len(bigram_ids)):
                    if config_ids[j] == bigram_ids[i]:
                        search_index.append(i)
                if len(search_index) == 0:
                    self.shared_weights = self.shared_weights.append({'bigram_id': config_ids[j],
                                                                      'weights': layer.get_weights()},
                                                                     ignore_index=True)
                else:
                    self.shared_weights.at[search_index[0], 'weights'] = layer.get_weights()
                j += 1
        self.shared_weights.to_pickle(self.weights_file)

    def set_model_weights(self, model):
        layer_configs = ['input']
        for layer in model.layers:
            if 'flatten' in layer.name:
                layer_configs.append(('flatten'))
            elif 'dropout' not in layer.name:
                layer_configs.append((layer.get_config()['units'], layer.get_config()['activation']))
        config_ids = []
        for i in range(1, len(layer_configs)):
            config_ids.append((layer_configs[i - 1], layer_configs[i]))
        j = 0
        for i, layer in enumerate(model.layers):
            if 'dropout' not in layer.name:
                warnings.simplefilter(action='ignore', category=FutureWarning)
                bigram_ids = self.shared_weights['bigram_id'].values
                search_index = []
                for i in range(len(bigram_ids)):
                    if config_ids[j] == bigram_ids[i]:
                        search_index.append(i)
                if len(search_index) > 0:
                    print("Transferring weights for layer:", config_ids[j])
                    layer.set_weights(self.shared_weights['weights'].values[search_index[0]])
                j += 1

    def train_model(self, model, x_data, y_data, nb_epochs, validation_split=0.1, callbacks=None):
        if self.nas_one_shot:
            self.set_model_weights(model)
            print(model.summary())
            history = model.fit(x_data,
                                y_data,
                                epochs=nb_epochs,
                                validation_split=validation_split,
                                callbacks=callbacks,
                                verbose=0)
            self.update_weights(model)
        else:
            history = model.fit(x_data,
                                y_data,
                                epochs=nb_epochs,
                                validation_split=validation_split,
                                callbacks=callbacks,
                                verbose=0)
        return history
