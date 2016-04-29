#!/usr/bin/env python3
import json
import re

import requests


class StanfordCoreNLP:
    """
    This class is originally developed by Smitha Milli, and modified by Heetae Kim
    in order to support unicode data and meet the our project needs.
    """

    def __init__(self, server_url='http://192.241.215.92:8011'):
        """
        You can specify your own server URL here if you have one.
        :param server_url: URL to the CoreNLP server.
        The default is http://192.241.215.92:8011.
        """
        assert isinstance(server_url, str)
        self.server_url = server_url

    def _annotate(self, text, properties):
        """
        Sends a RESTful API call to the CoreNLP server.
        :param text: A text data to be processed.
        :param properties: Properties that are attached to the url.
        :return: A JSON text.
        """
        assert isinstance(text, str)
        assert isinstance(properties, dict)

        # Checks that the Stanford CoreNLP server is started.
        try:
            requests.get(self.server_url)
        except requests.exceptions.ConnectionError:
            raise Exception('Check whether you have started the CoreNLP server.')

        # texts should be encoded to deal with unicode.
        # maximum length of data is 100k.
        data = text.encode()
        r = requests.post(self.server_url, params={'properties': str(properties)}, data=data,
                          headers={'Connection': 'close'})
        output = r.text
        output = json.loads(output, encoding='utf-8', strict=True)
        return output

    def parse(self, text):
        """
        Stanford CoreNLP parses texts and returns tokens
        and their corresponding POS tags.
        :param text: Input texts that are less than 100,000 bytes.
        :return: A tuple (list of words, list of POS tags)
        """
        assert isinstance(text, str)
        if text.strip() == '':
            return [], []

        output = self._annotate(text, properties={
            "annotators": "tokenize,ssplit,pos",
            "coref.md.type": "dep",
            "coref.mode": "statistical"
        })

        words = []
        postags = []

        for sentence in output['sentences']:
            for token in sentence['tokens']:
                word = token['word']
                pos = token['pos']
                word = re.sub(r'\s', '', word)
                words.append(word)
                postags.append(pos)
        return words, postags

    def split_sentences(self, text):
        """
        Stanford CoreNLP parses texts and returns sentences as a list
        :param text: Input texts that are less than 100,000 bytes.
        :return: A list of sentences.
        """
        assert isinstance(text, str)
        text = text.replace('\n', '')

        if text.strip() == '':
            return []

        output = self._annotate(text, properties={
            "annotators": "tokenize,ssplit",
            "coref.md.type": "dep",
            "coref.mode": "statistical"
        })

        sentences = []
        for sentence in output['sentences']:
            num_token = len(sentence['tokens'])
            start_index = sentence['tokens'][0]['characterOffsetBegin']
            end_index = sentence['tokens'][num_token - 1]['characterOffsetEnd']
            sentences.append(text[start_index:end_index])
        return sentences
