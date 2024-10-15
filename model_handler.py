import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()

BASE_MODEL_NAME = os.getenv('base_model_name')

MODEL_HIDDEN_SIZE = int(os.getenv('model_hidden_size'))
MODEL_OUTPUT_SIZE = int(os.getenv('model_output_size'))
MODEL_DROPOUT_PROB = float(os.getenv('model_dropout_prob'))

MODEL_FILE_NAME = os.getenv('model_file_name')
ENCODING_MAX_LENGTH = int(os.getenv('encoding_max_length'))

TOKENIZER = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)
BASE_MODEL = AutoModel.from_pretrained(BASE_MODEL_NAME)


class RegressionModel(nn.Module):
    def __init__(self, base_model, hidden_size=MODEL_HIDDEN_SIZE, output_size=MODEL_OUTPUT_SIZE, dropout_prob=MODEL_DROPOUT_PROB):
        super(RegressionModel, self).__init__()
        self.base_model = base_model
        self.dropout = nn.Dropout(dropout_prob)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, input_ids, attention_mask):
        outputs = self.base_model(input_ids=input_ids, attention_mask=attention_mask)
        cls_output = outputs.last_hidden_state[:, 0, :]
        cls_output = self.dropout(cls_output)
        output = self.fc(cls_output)
        return output


MODEL = RegressionModel(BASE_MODEL)
checkpoint = torch.load(MODEL_FILE_NAME)
MODEL.load_state_dict(checkpoint['model_state_dict'])
MODEL.eval()


def predict_texts(texts: list, max_len: int = ENCODING_MAX_LENGTH) -> list:
    """
    Предсказания на основе списка текстов.

    :param texts: Список текстов для предсказания.
    :param max_len: Максимальная длина текста для токенизации.
    :return: Список предсказаний.
    """
    predictions = []

    with torch.no_grad():
        for text in texts:
            encoding = TOKENIZER.encode_plus(
                text,
                add_special_tokens=True,
                max_length=max_len,
                return_token_type_ids=False,
                padding='max_length',
                truncation=True,
                return_attention_mask=True,
                return_tensors='pt'
            )

            input_ids = encoding['input_ids']
            attention_mask = encoding['attention_mask']

            output = MODEL(input_ids, attention_mask)
            prediction = output.squeeze().cpu().numpy()
            prediction = np.clip(prediction, -1, 1)

            predictions.append(prediction)

    return predictions