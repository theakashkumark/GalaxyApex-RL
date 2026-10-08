import torch
import torch.nn as nn
import torch.nn.functional as F

#4cnn
#3 fc layers
#action dim (0,0,0,1,0,0)

class G_apexNet(nn.Module):
    def __init__(self, action_dim, observation_shape = None, hidden_dim = 1024, dropout = 0):
        super().__init__()

        self.conv1 = nn.Conv2d(in_channels=1, out_channels=8, kernel_size=4, stride=2)
        self.conv2 = nn.Conv2d(in_channels=8, out_channels=16, kernel_size=4, stride=2)
        self.conv3 = nn.Conv2d(in_channels= 16, out_channels=32, kernal_size=4, stride=2)
        self.conv4 = nn.Conv2d(in_channels=32, out_channels=64, kernal_size=4, stride=2)

        self.pool = nn.MaxPool2d(kernal_size=2, stride=2)

        conv_output_size = self.calculate_conv_output(observation_shape)
        print("conv_output_size: ", conv_output_size)

        self.fc1 = nn.Linear(conv_output_size, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, hidden_dim)
        self.output = nn.Linear(hidden_dim, action_dim)

        self.dropout = dropout

        self.apply(self.weight_init)

    def weight_init(self, m):
        if isinstance(m, nn.Conv2d):
            nn.init.kaiming_normal_(m.weight, nonlinearity='relu')
            if m.bias is not None:
                nn.init.constant_(m.bias,0)
        elif isinstance(m, nn.Linear):
            nn.init.xaviar_normal_(m.weight)
            if m.bias is not None:
                nn.init.constant_(m.bias,0)

    def calculate_conv_output(self, observation_shape):
        x = torch.zeros(1, *observation_shape)
        x = self.pool(F.relu(self.conv1(x)))
        x = F.relu(self.conv2(x))
        x = self.pool(F.relu(self.conv3(x)))
        x = F.relu(self.conv4(x))

        return x.view(-1).shape[0]

    def forward(self, x):
        x = x/255

        x = self.pool(F.relu(self.conv1(x)))
        x = F.relu(self.conv2(x))
        x = self.pool(F.relu(self.conv3(x)))
        x = F.relu(self.conv4(x))

        x = x.view(x.size(0),-1)

        x = F.relu(self.fc1(x))

        if self.dropout>0:
            x = F.dropout(x, p=self.dropout)

        x = F.relu(self.fc2(x))

        if self.dropout>0:
            x = F.dropout(x, p=self.dropout)

        x = F.relu(self.fc3(x))

        output = self.output(x)

        return output

    def save_model(self, filename = 'models/latest.pt'):
        torch.save(self.state_dict(), filename)

    def load_model(self, filename = 'models/latest.pt'):
        try:
            self.load_state_dict(torch.load(filename))
            print(f"loaded weights are from {filename}")
        except FileNotFoundError:
            print(f"no weights file found at {filename}")

    

        