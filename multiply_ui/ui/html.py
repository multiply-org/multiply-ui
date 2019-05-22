from typing import List, Any, Callable, Dict


def html_table(data_rows: List[List[Any]],
               header_row: List[str] = None,
               title: str = None,
               converters: Dict[int, Callable[[Any], str]] = None):
    rows = []
    for data_row in data_rows:
        row = []
        for i in range(len(data_row)):
            item = converters[i](data_row[i]) if converters and i in converters else data_row[i]
            row.append(html_tag('td', value=item))
        ''.join(row)
        rows.append(html_tag('tr', '\n'.join(row)))
    rows = ''.join(rows)

    header = None
    if header_row:
        def th(item: str):
            return html_tag('th', value=item)

        header = f"<tr>{''.join(map(th, header_row))}</tr>"

    if header:
        html = (f"<table>\n"
                f"{header}\n"
                f"{rows}"
                f"</table>")
    else:
        html = (f"<table>\n"
                f"{rows}"
                f"</table>")

    if title:
        html = (f"<div>\n"
                f"<h4>{title}</h4>\n"
                f"{html}\n"
                f"</div>")

    return html


def html_tag(name: str, value: Any = None, attributes: Dict[str, Any] = None):
    if attributes:
        attrs = ' '.join(map(lambda key: f'{key}="{attributes[key]}"', attributes.keys()))
        return f"<{name} {attrs}>{value if value is not None else ''}</{name}>"
    else:
        return f"<{name}>{value if value is not None else ''}</{name}>"
