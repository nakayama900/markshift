# -*- coding: utf-8 -*-
from .renderer import Renderer
from io import StringIO
import html

class HtmlRenderer(Renderer):
    def __init__(self, ):
        pass

    def render(self, elem):
        io = StringIO()
        for el in elem.child_elements:
            io.write(el.render())
        if len(elem.child_lines) > 0:
            # io.write('<div class=tab>')
            io.write('<ul>')
            for line in elem.child_lines:
                # io.write(line.render() + '<br/>')
                l = line.render() 
                if l == '':
                    io.write('<li class="empty-line">' + l + '<br/></li>')
                else:
                    io.write('<li>' + l + '</li>')
            # io.write('</div>')
            io.write('</ul>')
        tmp = io.getvalue()
        # print('render: '+ tmp)
        return tmp

    def render_line(self, elem):
        io = StringIO()
        for el in elem.child_elements:
            io.write(el.render())
        if len(elem.child_lines) > 0:
            # io.write('<div class=tab>')
            io.write('<ul>')
            for line in elem.child_lines:
                # io.write(line.render() + '<br/>')
                l = line.render() 
                if l == '':
                    io.write('<li class="empty-line">' + l + '<br/></li>')
                else:
                    io.write('<li>' + l + '</li>')
            # io.write('</div>')
            io.write('</ul>')
        return io.getvalue()

    def render_link(self, elem):
        io = StringIO()
        io.write(f'<a href="{elem.link}">{elem.content}</a>')
        return io.getvalue()

    def render_text(self, elem):
        return elem.content

    def render_strong(self, elem):
        io = StringIO()
        io.write('<b>')
        for el in elem.child_elements:
            io.write(el.render())
        io.write('</b>')
        return io.getvalue()

    def render_italic(self, elem):
        io = StringIO()
        io.write('<i>')
        for el in elem.child_elements:
            io.write(el.render())
        io.write('</i>')
        return io.getvalue()

    def render_math(self, elem):
        io = StringIO()
        if elem.inline == True:
            # io.write(f'<div id={elem.uid}/>')
            io.write('$$ ')
            io.write(elem.content)
            io.write(' $$')
            # io.write('</div>')
        else:
            io.write('[[ ')
            for line in elem.child_lines:
                io.write(line.render())
                io.write('\n')
            io.write(' ]]')
        return io.getvalue()

    def render_raw(self, elem):
        # TODO html escape
        return html.escape(elem.content)

    def render_quote(self, elem):
        io = StringIO()
        io.write('<blockquote>')
        for line in elem.child_lines:
            io.write(line.render() + '<br/>')
        io.write('</blockquote>')
        return io.getvalue()

    def render_code(self, elem):
        io = StringIO()
        io.write('<pre><code class="')
        io.write(elem.lang)
        io.write('">')
        for line in elem.child_lines:
            io.write(line.render())
            io.write('\n')
        io.write('</code></pre>')
        return io.getvalue()

    def render_img(self, elem):
        io = StringIO()
        io.write(f'<img src="{elem.src}" alt="{elem.alt}"/>')
        return io.getvalue()