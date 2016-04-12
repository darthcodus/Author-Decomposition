#!/usr/bin/env python3
import json
import requests


class StanfordCoreNLP:
    def __init__(self, server_url):
        if server_url[-1] == '/':
            server_url = server_url[:-1]
        self.server_url = server_url

    def annotate(self, text, properties):
        assert isinstance(text, str)
        assert isinstance(properties, dict)

        # Checks that the Stanford CoreNLP server is started.
        try:
            requests.get(self.server_url)
        except requests.exceptions.ConnectionError:
            raise Exception(
                'Check whether you have started the CoreNLP server e.g.\n'
                '$ cd stanford-corenlp \n'
                '$ java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer'
            )

        # texts should be encoded to deal with unicode.
        # maximum length of data is 100k.
        data = text.encode()
        r = requests.post(self.server_url, params={'properties': str(properties)}, data=data)
        output = r.text
        output = json.loads(output, encoding='utf-8', strict=True)
        return output

    def parse(self, texts):
        assert isinstance(texts, str)
        output = self.annotate(texts, properties={
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
                words.append(word)
                postags.append(pos)
        return words, postags
