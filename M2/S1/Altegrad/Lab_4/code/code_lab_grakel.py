import numpy as np
import re
from nltk.stem.porter import PorterStemmer
import warnings
import networkx as nx
import matplotlib.pyplot as plt
from grakel.utils import graph_from_networkx
from grakel.kernels import WeisfeilerLehman, VertexHistogram
from grakel.kernels import ShortestPath, RandomWalk, PyramidMatch
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

warnings.filterwarnings("ignore")


def load_file(filename):
    labels = []
    docs = []

    with open(filename, encoding="utf8", errors="ignore") as f:
        for line in f:
            content = line.split(":")
            labels.append(content[0])
            docs.append(content[1][:-1])

    return docs, labels


def clean_str(string):
    string = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", string)
    string = re.sub(r"\'s", " 's", string)
    string = re.sub(r"\'ve", " 've", string)
    string = re.sub(r"n\'t", " n't", string)
    string = re.sub(r"\'re", " 're", string)
    string = re.sub(r"\'d", " 'd", string)
    string = re.sub(r"\'ll", " 'll", string)
    string = re.sub(r",", " , ", string)
    string = re.sub(r"!", " ! ", string)
    string = re.sub(r"\(", " \( ", string)
    string = re.sub(r"\)", " \) ", string)
    string = re.sub(r"\?", " \? ", string)
    string = re.sub(r"\s{2,}", " ", string)
    return string.strip().lower().split()


def preprocessing(docs):
    preprocessed_docs = []
    n_sentences = 0
    stemmer = PorterStemmer()

    for doc in docs:
        clean_doc = clean_str(doc)
        preprocessed_docs.append([stemmer.stem(w) for w in clean_doc])

    return preprocessed_docs


def get_vocab(train_docs, test_docs):
    vocab = dict()

    for doc in train_docs:
        for word in doc:
            if word not in vocab:
                vocab[word] = len(vocab)

    for doc in test_docs:
        for word in doc:
            if word not in vocab:
                vocab[word] = len(vocab)

    return vocab


path_to_train_set = "./data/train_5500_coarse.label"
path_to_test_set = "./data/TREC_10_coarse.label"

# Read and pre-process train data
train_data, y_train = load_file(path_to_train_set)
train_data = preprocessing(train_data)

# Read and pre-process test data
test_data, y_test = load_file(path_to_test_set)
test_data = preprocessing(test_data)

# Extract vocabulary
vocab = get_vocab(train_data, test_data)
print("Vocabulary size: ", len(vocab))


# Task 11


def create_graphs_of_words(docs, vocab, window_size):
    graphs = list()
    for idx, doc in enumerate(docs):
        G = nx.Graph()

        ##################
        # your code here #
        ##################

        for i in range(len(doc)):
            for j in range(i + 1, min(i + window_size, len(doc))):
                w1 = doc[i]
                w2 = doc[j]
                if G.has_edge(w1, w2):
                    G[w1][w2]["weight"] += 1
                else:
                    G.add_edge(w1, w2, weight=1)
        # Ensure every node has a label attribute required by Grakel
        # Use integer vocab ids for labels so numeric kernels (e.g. ShortestPathAttr)
        # can operate without dtype errors. Also keep the token string in 'token'.
        for n in G.nodes():
            node_label = vocab.get(n, 0)
            G.nodes[n]["label"] = node_label
            G.nodes[n]["labels"] = node_label
            G.nodes[n]["token"] = n

        graphs.append(G)

    return graphs


# Create graph-of-words representations
G_train_nx = create_graphs_of_words(train_data, vocab, 3)
G_test_nx = create_graphs_of_words(test_data, vocab, 3)

print("Example of graph-of-words representation of document")
nx.draw_networkx(G_train_nx[3], with_labels=True)
plt.show()


# Task 12

# Transform networkx graphs to grakel representations
G_train = graph_from_networkx(G_train_nx, node_labels_tag="label")
G_test = graph_from_networkx(G_test_nx, node_labels_tag="label")

# Initialize a Weisfeiler-Lehman subtree kernel
# - n_iter=1: One iteration of WL refinement
# - normalize=False: Don't normalize the kernel matrix
# - base_graph_kernel=VertexHistogram: Use vertex histogram as base kernel
gk = WeisfeilerLehman(n_iter=5, normalize=False, base_graph_kernel=VertexHistogram)

# Construct kernel matrices
K_train = gk.fit_transform(G_train)
K_test = gk.transform(G_test)

# Task 13

# Train an SVM classifier and make predictions
clf = SVC(kernel="precomputed")
clf.fit(K_train, y_train)
y_pred = clf.predict(K_test)

# Evaluate the predictions
accuracy = accuracy_score(y_pred, y_test)
print("Accuracy:", accuracy)


# Task 14
print("\n=== Experimenting with Different Kernels ===\n")

# 1. Shortest Path Kernel
print("1. Shortest Path Kernel:")
gk_sp = ShortestPath(normalize=True)
K_train_sp = gk_sp.fit_transform(G_train)
K_test_sp = gk_sp.transform(G_test)

clf_sp = SVC(kernel="precomputed")
clf_sp.fit(K_train_sp, y_train)
y_pred_sp = clf_sp.predict(K_test_sp)
accuracy_sp = accuracy_score(y_pred_sp, y_test)
print(f"   Accuracy: {accuracy_sp:.4f}")

# 2. Random Walk Kernel
print("\n2. Random Walk Kernel:")
gk_rw = RandomWalk(normalize=True, lamda=0.01)
K_train_rw = gk_rw.fit_transform(G_train)
K_test_rw = gk_rw.transform(G_test)

clf_rw = SVC(kernel="precomputed")
clf_rw.fit(K_train_rw, y_train)
y_pred_rw = clf_rw.predict(K_test_rw)
accuracy_rw = accuracy_score(y_pred_rw, y_test)
print(f"   Accuracy: {accuracy_rw:.4f}")

# 3. Weisfeiler-Lehman with more iterations
print("\n3. Weisfeiler-Lehman (3 iterations):")
gk_wl3 = WeisfeilerLehman(n_iter=3, normalize=True, base_graph_kernel=VertexHistogram)
K_train_wl3 = gk_wl3.fit_transform(G_train)
K_test_wl3 = gk_wl3.transform(G_test)

clf_wl3 = SVC(kernel="precomputed")
clf_wl3.fit(K_train_wl3, y_train)
y_pred_wl3 = clf_wl3.predict(K_test_wl3)
accuracy_wl3 = accuracy_score(y_pred_wl3, y_test)
print(f"   Accuracy: {accuracy_wl3:.4f}")

# 4. Weisfeiler-Lehman with normalization
print("\n4. Weisfeiler-Lehman (1 iteration, normalized):")
gk_wl_norm = WeisfeilerLehman(
    n_iter=1, normalize=True, base_graph_kernel=VertexHistogram
)
K_train_wl_norm = gk_wl_norm.fit_transform(G_train)
K_test_wl_norm = gk_wl_norm.transform(G_test)

clf_wl_norm = SVC(kernel="precomputed")
clf_wl_norm.fit(K_train_wl_norm, y_train)
y_pred_wl_norm = clf_wl_norm.predict(K_test_wl_norm)
accuracy_wl_norm = accuracy_score(y_pred_wl_norm, y_test)
print(f"   Accuracy: {accuracy_wl_norm:.4f}")

# Summary
print("\n=== Summary ===")
results = {
    "Weisfeiler-Lehman (1 iter, no norm)": accuracy,
    "Weisfeiler-Lehman (1 iter, normalized)": accuracy_wl_norm,
    "Weisfeiler-Lehman (3 iters, normalized)": accuracy_wl3,
    "Shortest Path": accuracy_sp,
    "Random Walk": accuracy_rw,
}

for kernel_name, acc in sorted(results.items(), key=lambda x: x[1], reverse=True):
    print(f"{kernel_name:40s}: {acc:.4f}")
