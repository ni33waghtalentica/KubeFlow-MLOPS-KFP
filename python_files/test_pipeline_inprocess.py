#!/usr/bin/env python3
"""Run the same Iris ML workflow in-process (no containers). Use for testing when Docker is unavailable."""
import sys

def main():
    try:
        from sklearn.datasets import load_iris
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score
    except ImportError:
        print("ERROR: scikit-learn required. Run: pip install scikit-learn")
        sys.exit(1)

    iris = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        iris.data, iris.target, test_size=0.2
    )
    clf = RandomForestClassifier()
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Model accuracy: {acc}")
    return float(acc)

if __name__ == "__main__":
    acc = main()
    sys.exit(0)
