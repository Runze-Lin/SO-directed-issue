# SO-directed-issue
training a model to solve SO-directed issue


The issue tracker on GitHub is designed to track ideas, enhancements, tasks, and bugs for software project maintainers to address. In contrast, Stack Overflow is a Q&A forum intended for specific programming questions from programmers of all levels of expertise. Despite the clear differences between these two platforms, a common issue arises when questions more suited for Stack Overflow, such as those asking how to implement a function using a specific library, are posted on GitHub’s issue tracker. Developers often redirect these support questions to Stack Overflow as they do not report bugs or propose features. These Stack Overflow-directed issues consume developers’ time and leave the original question unanswered.  

The study investigates the characteristics and trends of Stack Overflow-oriented questions on GitHub’s issue tracker and developed several deep learning models to classify questions posted in the future automatically. The best model got a test accuracy of up to 76.2%. the results of this study emphasize the importance of properly categorizing questions on online platforms. By utilizing deep learning models to automatically classify questions, developers can more efficiently address issues and ensure that questions are directed to the appropriate platform. This, in turn, can lead to quicker and more effective resolutions to programming-related issues.



The project consists of several steps: data collecting, data labeling, data preprocessing, LSTM training, and BERT finetuning. Each step is implemented in a separate Python or Jupyter notebook file, as described below. 
 
- The file collectPRinfo.py performs data crawling from GitHub pull requests and stores the results in txt files. 
- The file USC_labeling.ipynb performs data labeling using a heuristic based on the pull request status and comments. It takes the txt files from the previous step as input and outputs a CSV file with labels. 
- The file training_dataset_generation.ipynb performs data preprocessing on the labeled CSV file and the original txt files. It splits the data into training, validation, and testing sets, and applies some data-cleaning techniques such as tokenization and punctuation removal. 
- The file LSTM_dataset_gen.ipynb performs additional preprocessing on the training set for the LSTM model.  
- The file LSTM_model.ipynb implements and trains an LSTM model on the preprocessed training set. It evaluates the model on the validation and testing sets and reports the performance metrics. 
- The file BERT_colab_final_version.ipynb implements and finetunes a BERT model on the original training set (from training_dataset_generation.ipynb). It evaluates the model on the validation and testing sets and reports the performance metrics. 
 
Due to the size limitation of GitHub, we have upload the crawled data to Google Drive: [https://drive.google.com/drive/folders/1TEemMON2rPt9iJ1zhVlNODNy2CxMkLHm?usp=sharing] .We have also uploaded the training dataset file to Google Drive: [https://drive.google.com/drive/folders/1PYgi42qvHJDgDwEr-SxJmhvPPXwl81nI?usp=sharing]. This file contains the labeled data. 
