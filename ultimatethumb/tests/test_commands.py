from ultimatethumb.commands import PngquantCommand


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
