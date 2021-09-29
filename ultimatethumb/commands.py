from command_executor import Command
from django.conf import settings


class GraphicsmagickCommand(Command):
    """
    Command to call gm (Graphicsmagick) to generate thumbnails.
    """

    required_parameters = ['infile', 'outfile']

    command = '{GM_BIN} convert "{infile}" {options} "{outfile}"'

    def get_parameters(self):
        GM_BIN = getattr(settings, 'ULTIMATETHUMB_GRAPHICSMAGICK_BINARY', 'gm')

        options = self.parameters.get('options', {'noop': True})

        return {
            'GM_BIN': GM_BIN,
            'infile': self.parameters['infile'],
            'outfile': self.parameters['outfile'],
            'options': ' '.join(
                [
                    '{0}{1}'.format(
                        key if key[0] == '+' else '-{0}'.format(key),
                        '' if value is True else ' {0}'.format(value),
                    )
                    for key, value in options.items()
                ]
            ),
        }


class PngquantCommand(Command):
    """
    Command to call pngquant to improve the file size of png files.
    """

    ignore_output = True
    fail_silently = True
    required_parameters = ['pngfile', 'quality']

    command = '{PNGQUANT_BIN} -f --ext .png --quality {quality} "{pngfile}"'

    def get_parameters(self):
        PNGQUANT_BIN = getattr(settings, 'ULTIMATETHUMB_PNGQUANT_BINARY', 'pngquant')

        return {
            'PNGQUANT_BIN': PNGQUANT_BIN,
            'pngfile': self.parameters['pngfile'],
            'quality': self.parameters['quality'],
        }
