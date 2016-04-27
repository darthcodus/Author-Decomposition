#!/usr/bin/env python3
import glob
import os
from unittest import TestCase

from authorclustering.corenlp import StanfordCoreNLP


class StanfordCoreNLPTest(TestCase):
    def setUp(self):
        self.nlp = StanfordCoreNLP('http://192.241.215.92:8011')

    def test_split_sentences(self):
        chunks = []
        texts = ''

        input_path = '../corpora/spanish_blogs/*/*'
        for file_path in glob.glob(input_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    if len(texts) + len(line) >= 90000:
                        chunks.append(texts)
                        texts = ''
                    texts += line
        chunks.append(texts)

        sentences = []
        for chunk in chunks:
            sentences.extend(self.nlp.split_sentences(chunk))

        with open('test_split_sentences.txt', 'w', encoding='utf-8') as file:
            for s in sentences:
                file.write(s + '\n')
        self.assertTrue(os.path.isfile('test_split_sentences.txt'))

    def test_parse(self):
        nlp = StanfordCoreNLP('http://localhost:8011')
        nlp.parse('Por presupuesto, calidad, historia y escenario. Otra cosa con el 1-1 en la mochila y esta plantilla sería catastrófico.A la pizarra vuelve la ficha maestra, Cristiano Ronaldo. Y seguramente que esto le muestre el camino de banco a un Adebayor que, aunque bregador como en pocos tramos de su carrera, debería dejar su sitio a un Benzema de dulce. En la ida desatascó el asunto en un ramalazo de nueve y se confía en él para hacer lo propio en la vuelta. Además el galo se entiende bien con Cristiano. Son dos nueves invisibles, distantes de la ortodoxia que pide la camiseta y precisamente por ello temibles. En particular se espera que un Cristiano fresco tenga la llave que la abra al Madrid la puerta de cuartos. Para volver a pasear por los pasillos nobles de la que siempre ha sido su casa.El resto deberán aportar movilidad a la receta. El centro del campo del Olympique no aguanta la comparación técnica con el merengue pero es correoso y sacrificado como pocos. Son chicles en la suela durante un día de verano y el Madrid deberá moverse y mover para asomarse a los huecos. Ya saben, a lo que digan Xabi y Özil. Atrás habrá tirar de retrovisor para pegarse a un listo como Lisandro y no permitir ni una alegría a balón parado. Clave puede ser esto último si hay cromos como Pjanic (que quizá sustituya al tocado Gorcouff) de por medio.El Madrid es favorito por historia juego y factor campo aunque las dificultades que siempre se han encontrado frente al Lyon no deben menospreciarse a la hora de la apuesta. bwin.com paga 1.35 € por la victoria del Madrid y 7.75 € por la del club francés. Números cantán. La clasificación gala se paga a 5. 25 euros.')

if __name__ == '__main__':
    nosetest.main()
