from barbeque.commands.base import Command
from django.conf import settings


class PngquantCommand(Command):
    ignore_output = True
    fail_silently = True
    required_parameters = ['pngfile', 'quality']

    command = (
        '{PNGQUANT_BIN}'
        ' -f'
        ' --ext .png'
        ' --quality {quality}'
        ' "{pngfile}"'
    )

    def get_parameters(self):
        PNGQUANT_BIN = getattr(settings, 'ULTIMATETHUMB_PNGQUANT_BINARY', 'pngquant')

        return {
            'PNGQUANT_BIN': PNGQUANT_BIN,
            'pngfile': self.parameters['pngfile'],
            'quality': self.parameters['quality'],
        }
