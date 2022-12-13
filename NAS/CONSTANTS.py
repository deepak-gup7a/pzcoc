########################################################
#                   NAS PARAMETERS                     #
########################################################
CONTROLLER_SAMPLING_EPOCHS = 10
SAMPLES_PER_CONTROLLER_EPOCH = 10
CONTROLLER_TRAINING_EPOCHS = 10
ARCHITECTURE_TRAINING_EPOCHS = 10
CONTROLLER_LOSS_ALPHA = 0.9

########################################################
#               CONTROLLER PARAMETERS                  #
########################################################
OPTIMIZER_ADAM = 'Adam'
CONTROLLER_LSTM_DIM = 100
CONTROLLER_OPTIMIZER = OPTIMIZER_ADAM
CONTROLLER_LEARNING_RATE = 0.01
CONTROLLER_DECAY = 0.1
CONTROLLER_MOMENTUM = 0.0
CONTROLLER_USE_PREDICTOR = True

########################################################
#                   NAS PARAMETERS                     #
########################################################
CATEGORICAL_CROSSENTROPY = 'categorical_crossentropy'
MAX_ARCHITECTURE_LENGTH = 10
NAS_OPTIMIZER = OPTIMIZER_ADAM
NAS_LEARNING_RATE = 0.01
NAS_DECAY = 0.0
NAS_MOMENTUM = 0.0
NAS_DROPOUT = 0.2
NAS_LOSS_FUNCTION = CATEGORICAL_CROSSENTROPY
NAS_ONE_SHOT = True

########################################################
#                   DATA PARAMETERS                    #
########################################################
TARGET_CLASSES = 2

########################################################
#                  OUTPUT PARAMETERS                   #
########################################################
TOP_N = 5
