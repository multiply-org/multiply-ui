import unittest

from multiply_ui.util.html import html_table, html_element


class HtmlTest(unittest.TestCase):
    def test_html_element(self):
        self.assertEqual('<p></p>',
                         html_element('p'))
        self.assertEqual('<p>42</p>',
                         html_element('p', value=42))
        self.assertEqual('<img style="background-color:red" src="bibo.png"></img>',
                         html_element('img', att=dict(style='background-color:red',
                                                      src='bibo.png')))
        self.assertEqual('<a href="bibo.png">Bibo</a>',
                         html_element('a', dict(href='bibo.png'), 'Bibo'))

    def test_html_table(self):
        self.assertEqual('<table></table>',
                         html_table([]))
        self.assertEqual('<table>'
                         '<tr><td>1</td><td>2</td><td>3</td></tr>'
                         '<tr><td>4</td><td>5</td><td>6</td></tr>'
                         '</table>',
                         html_table([[1, 2, 3], [4, 5, 6]]))
        self.assertEqual('<table>'
                         '<tr><th>A</th><th>B</th><th>C</th></tr>'
                         '<tr><td>1</td><td>2</td><td>3</td></tr>'
                         '<tr><td>4</td><td>5</td><td>6</td></tr>'
                         '</table>',
                         html_table([[1, 2, 3], [4, 5, 6]],
                                    header_row=['A', 'B', 'C']))
        self.assertEqual('<div>'
                         '<h4>Results</h4>'
                         '<table>'
                         '<tr><th>A</th><th>B</th><th>C</th></tr>'
                         '<tr><td>1</td><td>2</td><td>3</td></tr>'
                         '<tr><td>4</td><td>5</td><td>6</td></tr>'
                         '</table>'
                         '</div>',
                         html_table([[1, 2, 3], [4, 5, 6]],
                                    header_row=['A', 'B', 'C'],
                                    title='Results'))

    def test_html_table_with_converter(self):
        def converter_0(item):
            return f'+{item}'

        def converter_1(item):
            return f'{item}!'

        def converter_2(item):
            return f'{item}?'

        self.assertEqual('<table>'
                         '<tr><td>+1</td><td>+2</td><td>+3</td></tr>'
                         '<tr><td>+4</td><td>+5</td><td>+6</td></tr>'
                         '</table>',
                         html_table([[1, 2, 3], [4, 5, 6]],
                                    col_converter=converter_0))

        self.assertEqual('<table>'
                         '<tr><td>+1</td><td>2!</td><td>3?</td></tr>'
                         '<tr><td>+4</td><td>5!</td><td>6?</td></tr>'
                         '</table>',
                         html_table([[1, 2, 3], [4, 5, 6]],
                                    col_converter=[converter_0, converter_1, converter_2]))

        self.assertEqual('<table>'
                         '<tr><td>1</td><td>2!</td><td>3</td></tr>'
                         '<tr><td>4</td><td>5!</td><td>6</td></tr>'
                         '</table>',
                         html_table([[1, 2, 3], [4, 5, 6]],
                                    col_converter={1: converter_1}))
