from collections import OrderedDict

from ultimatethumb.commands import GraphicsmagickCommand, PngquantCommand


class TestGraphicsmagickCommand:

    def test_get_command(self):
        options = OrderedDict()
        options['trueflag'] = True
        options['+falseflag'] = True
        options['valueflag'] = 'somevalue'

        cmd = GraphicsmagickCommand(infile='in.jpg', outfile='out.jpg', options=options)

        assert cmd.get_command() == [
            'gm',
            'convert',
            'in.jpg',
            '-trueflag',
            '+falseflag',
            '-valueflag', 'somevalue',
            'out.jpg'
        ]


class TestPngquantCommand:
    def test_get_command(self):
        cmd = PngquantCommand(pngfile='in.png', quality='75-90')

        assert cmd.get_command() == [
            'pngquant',
            '-f',
            '--ext', '.png',
            '--quality', '75-90',
            'in.png'
        ]
