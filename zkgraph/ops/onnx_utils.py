import numpy as np
from onnx import onnx_ml_pb2

type_to_proto_value_attr = {
    onnx_ml_pb2.AttributeProto.FLOAT: "f",
    onnx_ml_pb2.AttributeProto.INT: "i",
    onnx_ml_pb2.AttributeProto.STRING: "s",
    onnx_ml_pb2.AttributeProto.TENSOR: "t",
    onnx_ml_pb2.AttributeProto.GRAPH: "g",
    onnx_ml_pb2.AttributeProto.FLOATS: "floats",
    onnx_ml_pb2.AttributeProto.INTS: "ints",
    onnx_ml_pb2.AttributeProto.STRINGS: "strings",
    onnx_ml_pb2.AttributeProto.TENSORS: "tensors",
    onnx_ml_pb2.AttributeProto.GRAPHS: "graphs",
}


def get_proto_attribute_value(attribute: onnx_ml_pb2.AttributeProto):
    attr_type = attribute.type
    attr_name = type_to_proto_value_attr.get(attr_type)
    if attr_name:
        attribute_value = getattr(attribute, attr_name)

        if attr_name in ["ints", "floats"]:
            attribute_value = np.array(attribute_value)

        return attribute_value
    else:
        return None


def generate_small_iris_onnx_model(onnx_output_path="tests/assets/iris_model.onnx"):

    import torch
    import torch.nn as nn
    import torch.optim as optim
    from sklearn.datasets import load_iris
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler

    ### create a small sample onnx model
    iris = load_iris()
    X = iris.data[:100, [0, 2]]  # We only take the first two features for simplicity
    y = iris.target[:100]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    X_train = torch.FloatTensor(X_train)
    y_train = torch.LongTensor(y_train)
    X_test = torch.FloatTensor(X_test)
    y_test = torch.LongTensor(y_test)

    class SimpleNet(nn.Module):
        def __init__(self):
            super(SimpleNet, self).__init__()
            self.fc1 = nn.Linear(2, 10)
            self.fc2 = nn.Linear(10, 2)

        def forward(self, x):
            x = torch.relu(self.fc1(x))
            x = self.fc2(x)
            return x

    model = SimpleNet()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.01)

    # Train the model
    num_epochs = 100
    for epoch in range(num_epochs):
        outputs = model(X_train)
        loss = criterion(outputs, y_train)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if (epoch + 1) % 10 == 0:
            print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}")

    # Test the model
    with torch.no_grad():
        correct = 0
        total = 0
        outputs = model(X_test)
        _, predicted = torch.max(outputs.data, 1)
        total += y_test.size(0)
        correct += (predicted == y_test).sum().item()
        print(f"Accuracy: {100 * correct / total:.2f}%")

    # Convert to ONNX
    dummy_input = torch.randn(1, 2)
    torch.onnx.export(model, dummy_input, onnx_output_path)
