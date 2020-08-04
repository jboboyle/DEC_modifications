from datetime import datetime
import os
import sys
sys.path.insert(0, '../RISCluster/')

import importlib as imp
import production
imp.reload(production)
import utils
imp.reload(utils)

if __name__ == '__main__':
    # =========================================================================
    # Universal Parameters
    # =========================================================================
    # Select from 'pretrain', 'train', or 'predict':
    mode = 'predict'
    fname_dataset = '../../../Data/DetectionData.h5'
    savepath = '../../../Outputs/'
    indexpath = '/Users/williamjenkins/Research/Workflows/RIS_Clustering/Data/TraValIndex_M=500_Res=0.0_20200803T202014.pkl'
    # =========================================================================
    # Pre-Training Routine
    # =========================================================================
    if mode == 'pretrain':
        savepath_exp, serial_exp = utils.init_exp_env(mode, savepath)
        parameters = dict(
            fname_dataset=fname_dataset,
            device=utils.set_device(),
            indexpath=indexpath,
            n_epochs=10,
            savepath=savepath_exp,
            serial=serial_exp,
            show=False,
            send_message=False,
            mode=mode,
            early_stopping=True,
            patience=1
        )
        hyperparameters = dict(
            batch_size=[256, 512],
            lr=[0.0001, 0.001]
        )
        utils.save_exp_config(
            savepath_exp,
            serial_exp,
            parameters,
            hyperparameters
        )
        production.DCEC_pretrain(parameters, hyperparameters)
    # =========================================================================
    # Training Routine
    # =========================================================================
    if mode == 'train':
        savepath_exp, serial_exp = utils.init_exp_env(mode, savepath)
        parameters = dict(
            fname_dataset=fname_dataset,
            device=utils.set_device(),
            indexpath=indexpath,
            n_epochs=10,
            n_clusters=11,
            update_interval=5,
            savepath=savepath_exp,
            serial=serial_exp,
            show=False,
            send_message=False,
            mode=mode,
            saved_weights='/Users/williamjenkins/Research/Workflows' + \
                '/RIS_Clustering/Outputs/Models/AEC/Exp20200802T013941' + \
                '/Run_BatchSz=512_LR=0.0001/AEC_Params_20200802T061234.pt'
        )
        hyperparameters = dict(
            batch_size=[256, 512],
            lr=[0.0001, 0.001],
            gamma=[0.1],
            tol=[0.01]
        )
        # hyperparameters = dict(
        #     batch_size = [128, 256, 512, 1024, 2048],
        #     lr = [0.00001, 0.0001, 0.001],
        #     gamma = [0.08, 0.1, 0.12],
        #     tol = [0.0001, 0.001, 0.01, 0.1]
        # )
        utils.save_exp_config(
            savepath_exp,
            serial_exp,
            parameters,
            hyperparameters
        )
        production.DCEC_train(parameters, hyperparameters)
    # =========================================================================
    # Prediction Routine
    # =========================================================================
    if mode == 'predict':
        savepath_exp, serial_exp = utils.init_exp_env(mode, savepath)
        parameters = dict(
            fname_dataset=fname_dataset,
            device=utils.set_device(),
            M = 500, # Select integer or 'all'
            indexpath=indexpath,
            exclude=True,
            batch_size=256,
            n_clusters=11,
            savepath=savepath_exp,
            serial=serial_exp,
            show=False,
            send_message=False,
            mode=mode,
            saved_weights='/Users/williamjenkins/Research/Workflows' + \
                '/RIS_Clustering/Outputs/Models/DCEC/Exp20200802T225523' + \
                '/Run_BatchSz=256_LR=0.001_gamma=0.1_tol=0.01/DCEC_Params_ ' +\
                '20200802T225531.pt',
            max_workers=14
        )
        utils.save_exp_config(savepath_exp, serial_exp, parameters, None)
        production.DCEC_predict(parameters)
# End of script.