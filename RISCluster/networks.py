#!/usr/bin/env python3

"""
William Jenkins
Scripps Institution of Oceanography, UC San Diego

This script contains neural network architectures used in the RIS package.
"""

import torch
import torch.nn as nn


# ======== This network is for data of dimension 100x87 (4 s) =================
class Encoder(nn.Module):
    """
    Description: Encoder layers of autoencoder model; encodes input data
    (spectrograms) into the latent feature space.
    Inputs:
        - Input data (spectrograms)
    Outputs:
        - Latent feature space data
    """
    def __init__(self):
        super(Encoder, self).__init__()
        self.encoder = nn.Sequential(
            nn.Conv2d(1, 8, kernel_size=(3,3), stride=(2,2), padding=(1,1)),
            nn.ReLU(True),
            nn.Conv2d(8, 16, kernel_size=(3,3), stride=(2,2), padding=(1,1)),
            nn.ReLU(True),
            nn.Conv2d(16, 32, kernel_size=(3,3), stride=(2,2), padding=(1,1)),
            nn.ReLU(True),
            nn.Conv2d(32, 64, kernel_size=(3,3), stride=(2,2), padding=(1,1)),
            nn.ReLU(True),
            nn.Conv2d(64, 128, kernel_size=(3,3), stride=(2,2), padding=(1,0)),
            nn.ReLU(True),

            nn.Flatten(),
            nn.Linear(1152, 9),
            nn.ReLU(True)
        )

    def forward(self, x):
        x = self.encoder(x)
        return x


class Decoder(nn.Module):
    """
    Description: Decoder layers of autoencoder model; reconstructs encoder
    inputs using the latent features generated by the encoder.
    Inputs:
        - Latent space data
    Outputs:
        - Reconstructed data
    """
    def __init__(self):
        super(Decoder, self).__init__()
        self.latent2dec = nn.Sequential(
            nn.Linear(9, 1152),
            nn.ReLU(True)
        )
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(128, 64, kernel_size=(3,3), stride=(2,2), padding=(1,0)), # <---- Experimental
            nn.ReLU(True),  # <---- Experimental
            nn.ConvTranspose2d(64, 32, kernel_size=(3,3), stride=(2,2), padding=(0,1)),
            nn.ReLU(True),
            nn.ConvTranspose2d(32, 16, kernel_size=(3,3), stride=(2,2), padding=(0,1)),
            nn.ReLU(True),
            nn.ConvTranspose2d(16, 8, kernel_size=(3,3), stride=(2,2), padding=(0,0)),
            nn.ReLU(True),
            nn.ConvTranspose2d(8, 1, kernel_size=(3,3), stride=(2,2), padding=(0,1)),
        )

    def forward(self, x):
        x = self.latent2dec(x)
        x = x.view(-1, 128, 3, 3)
        x = self.decoder(x)
        return x[:,:,4:-4,1:]


class AEC(nn.Module):
    """
    Description: Autoencoder model; combines encoder and decoder layers.
    Inputs:
        - Input data (spectrograms)
    Outputs:
        - Reconstructed data
        - Latent space data
    """
    def __init__(self):
        super(AEC, self).__init__()
        self.encoder = Encoder()
        self.decoder = Decoder()

    def forward(self, x):
        z = self.encoder(x)
        x = self.decoder(z)
        return x, z


def init_weights(m):
    """
    Description: Initializes weights with the Glorot Uniform distribution.
    Inputs:
        - Latent space data
    Outputs:
        - Reconstructed data
    """
    if type(m) in [nn.Linear, nn.Conv2d, nn.ConvTranspose2d]:
        torch.nn.init.xavier_uniform_(m.weight)
        m.bias.data.fill_(0.01)


class ClusteringLayer(nn.Module):
    """
    Description: Generates soft cluster assignments using latent features as
    input.
    Arguments:
        - n_clusters: User-defined
        - n_features: Must match output dimension of encoder.
        - alpha: Exponential factor (default: 1.0)
        - weights: Initial values for the cluster centroids
    Inputs:
        Encoded data (output of encoder)
    Outputs:
        Soft cluster assignments
    """
    def __init__(self, n_clusters, n_features=9, alpha=1.0, weights=None):
        super(ClusteringLayer, self).__init__()
        self.n_features = n_features
        self.n_clusters = n_clusters
        self.alpha = alpha
        if weights is None:
            initial_weights = torch.zeros(
                self.n_clusters, self.n_features, dtype=torch.float
            )
            nn.init.xavier_uniform_(initial_weights)
        else:
            initial_weights = weights
        self.weights = nn.Parameter(initial_weights)

    def forward(self, x):
        x = x.unsqueeze(1) - self.weights
        x = torch.mul(x, x)
        x = torch.sum(x, dim=2)
        x = 1.0 + (x / self.alpha)
        x = 1.0 / x
        x = x ** ((self.alpha +1.0) / 2.0)
        x = torch.t(x) / torch.sum(x, dim=1)
        x = torch.t(x)
        return x


class DCM(nn.Module):
    """
    Description: Deep Clustering Model; combines autoencoder with clustering
    layer to generate end-to-end deep embedded clustering neural network model.
    Arguments:
        - n_clusters: User-defined
    Inputs:
        - Input data (spectrograms)
    Outputs:
        - Soft cluster assignments
        - Reconstructed data
        - Latent space data
    """
    def __init__(self, n_clusters):
        super(DCM, self).__init__()
        self.n_clusters = n_clusters
        self.encoder = Encoder()
        self.decoder = Decoder()
        self.clustering = ClusteringLayer(self.n_clusters)

    def forward(self, x):
        z = self.encoder(x)
        x = self.decoder(z)
        q = self.clustering(z)
        return q, x, z
