from typing import List, Any, Callable, Dict, Union

Converter = Callable[[Any], Any]


def html_table(data_rows: List[List[Any]],
               header_row: List[str] = None,
               title: str = None,
               col_converter: Union[Converter, List[Converter], Dict[int, Converter]] = None):
    rows = []
    for data_row in data_rows:
        row = []
        for i in range(len(data_row)):
            item = data_row[i]
            if col_converter is not None:
                try:
                    convert = col_converter[i]
                except (TypeError, KeyError):
                    convert = col_converter
                try:
                    item = convert(item)
                except TypeError:
                    pass
            row.append(html_element('td', value=item))
        rows.append(html_element('tr', ''.join(row)))
    rows = ''.join(rows)

    header = None
    if header_row:
        def th(value: str):
            return html_element('th', value=value)

        header = f'<tr>{"".join(map(th, header_row))}</tr>'

    if header:
        html = (f'<table>'
                f'{header}'
                f'{rows}'
                f'</table>')
    else:
        html = (f'<table>'
                f'{rows}'
                f'</table>')

    if title:
        html = (f'<div>'
                f'<h4>{title}</h4>'
                f'{html}'
                f'</div>')

    return html


def html_element(name: str, value: Any = None, attributes: Dict[str, Any] = None):
    if attributes:
        attrs = ' '.join(map(lambda key: f'{key}="{attributes[key]}"', attributes.keys()))
        return f'<{name} {attrs}>{value if value is not None else ""}</{name}>'
    else:
        return f'<{name}>{value if value is not None else ""}</{name}>'
