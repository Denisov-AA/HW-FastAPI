import joblib
from sklearn.datasets import load_iris
from sklearn.ensemble import GradientBoostingClassifier


class ModelException(Exception):
    pass


class ClassifierModel:

    def __init__(self, path) -> None:
        self.path = path

    def create_model(self):
        try:
            iris = load_iris()
            X, y = iris.data, iris.target

            model = GradientBoostingClassifier()
            model.fit(X, y)

            joblib.dump(model, self.path + '/trained_model_gb.pkl')

        except Exception as exc:
            raise ModelException(
                f'Model creation failed: {exc}'
            ) from exc

    def predict(self, features):
        try:
            model = joblib.load(self.path + '/trained_model_gb.pkl')
            prediction = model.predict(features)
            return prediction[0]

        except Exception as exc:
            raise ModelException(
                f'Model prediction failed: {exc}'
            ) from exc


def get_ml_service(path):
    return ClassifierModel(path)
