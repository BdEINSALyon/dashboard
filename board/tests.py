from django.test import TestCase

from board import models
from board.models import Computer


class ComputerTestCase(TestCase):
    def setUp(self):
        ok_status = {
            'os': {
                'ram': {'total': 8283248, 'available': 6260676},
                'disk': {'total': 499867709440, 'available': 411422969856},
                'locked': [],
                'install_date': {'day': 29, 'hour': 12, 'year': 2017, 'month': 1, 'minute': 11, 'second': 34},
                'temp_profiles': 0,
                'total_sessions': 0
            },
            'apps': {
                'vlc': {
                    'icon': 'play',
                    'name': 'VLC',
                    'installed': True,
                    'mandatory': False,
                    'verification': {'type': 'path',
                                     'paths': ['C:\\Program Files\\VideoLAN']}},
                'office': {
                    'icon': 'file-word-o',
                    'name': 'Microsoft Office',
                    'installed': True,
                    'mandatory': True,
                    'verification': {'type': 'path',
                                     'paths': ['C:\\Program Files\\Microsoft Office\\Office16\\WINWORD.EXE',
                                               'C:\\Program Files (x86)\\Microsoft Office\\Office16\\WINWORD.EXE']}},
                'indesign': {
                    'icon': 'file-image-o',
                    'name': 'Adobe InDesign',
                    'installed': False,
                    'mandatory': False,
                    'verification': {'type': 'path',
                                     'paths': ['C:\\Program Files\\Adobe\\Adobe InDesign CC 2017']}},
                'premiere': {'icon': 'file-video-o',
                             'name': 'Adobe Premiere',
                             'installed': False,
                             'mandatory': False,
                             'verification': {'type': 'path',
                                              'paths': ['C:\\Program Files\\Adobe\\Adobe Premiere Pro CC 2017']}},
                'antivirus': {'icon': 'thermometer-3',
                              'name': 'Sophos Antivirus',
                              'installed': True,
                              'mandatory': True,
                              'verification': {'type': 'path',
                                               'paths': ['C:\\Program Files (x86)\\Sophos\\Sophos Anti-Virus']}},
                'photoshop': {'icon': 'file-image-o',
                              'name': 'Adobe Photoshop',
                              'installed': False,
                              'mandatory': False,
                              'verification': {'type': 'path',
                                               'paths': ['C:\\Program Files\\Adobe\\Adobe Photoshop CC 2017']}},
                'videoproj': {'icon': 'camera',
                              'name': 'Vidéoprojecteur Salle IF',
                              'installed': True,
                              'mandatory': False,
                              'verification': {'type': 'path',
                                               'paths': ['C:\\Program Files (x86)\\EPSON Projector']}},
                'illustrator': {'icon': 'file-image-o',
                                'name': 'Adobe Illustrator',
                                'installed': False,
                                'mandatory': False,
                                'verification': {'type': 'path',
                                                 'paths': ['C:\\Program Files\\Adobe\\Adobe Illustrator CC 2017']}},
                'adobe_reader': {
                    'icon': 'file-pdf-o',
                    'name': 'Adobe Reader',
                    'installed': True,
                    'mandatory': True,
                    'verification': {
                        'type': 'path',
                        'paths': [
                            'C:\\Program Files (x86)\\Adobe\\Acrobat Reader DC\\Reader\\AcroRd32.exe',
                            'C:\\Program Files (x86)\\Adobe\\Reader 11.0\\Reader\\AcroRd32.exe'
                        ]
                    }
                }
            },
            'tasks': {
                'shutdown': {'icon': 'power-off',
                             'name': 'Extinction automatique',
                             'installed': True,
                             'mandatory': True,
                             'verification': {'type': 'task',
                                              'task_names': ['shutdown']}},
                'delete_users': {'icon': 'user',
                                 'name': 'Suppression des utilisateurs',
                                 'installed': True,
                                 'mandatory': True,
                                 'verification': {'type': 'task',
                                                  'task_names': ['delete user profiles']}}
            },
            'network': {'ip': '134.214.129.44', 'mac': '80:ee:73:99:7b:47', 'dhcp': True},
            'name': 'BDE608-D01',
            'description': 'Shuttle tableau pas mur',
            'imprimante_ma': True,
            'windows_activation': True
        }
        Computer.objects.create(name='BDE608-D01', status=ok_status)

    def test_computer_is_ok(self):
        d01 = Computer.objects.get(name='BDE608-D01')
        self.assertTrue(d01.is_ok())

    def test_computer_too_much_ram(self):
        d01 = Computer.objects.get(name='BDE608-D01')
        d01.status['os']['ram']['available'] = 1
        self.assertFalse(d01.is_ok())

    def test_computer_too_much_disk(self):
        d01 = Computer.objects.get(name='BDE608-D01')
        d01.status['os']['disk']['available'] = 1
        self.assertFalse(d01.is_ok())

    def test_computer_not_activated(self):
        d01 = Computer.objects.get(name='BDE608-D01')
        d01.status['windows_activation'] = False
        self.assertFalse(d01.is_ok())

    def test_computer_no_printer(self):
        d01 = Computer.objects.get(name='BDE608-D01')
        d01.status['imprimante_ma'] = False
        self.assertFalse(d01.is_ok())

    def test_computer_no_dhcp(self):
        d01 = Computer.objects.get(name='BDE608-D01')
        d01.status['network']['dhcp'] = False
        self.assertFalse(d01.is_ok())

    def test_computer_too_much_temp(self):
        d01 = Computer.objects.get(name='BDE608-D01')
        d01.status['os']['temp_profiles'] = models.TEMP_PROFILES_DANGER + 1
        self.assertFalse(d01.is_ok())

    def test_computer_one_app_not_installed(self):
        d01 = Computer.objects.get(name='BDE608-D01')
        d01.status['apps']['office']['installed'] = False
        d01.status['apps']['office']['mandatory'] = True
        self.assertFalse(d01.is_ok())

    def test_computer_one_task_not_installed(self):
        d01 = Computer.objects.get(name='BDE608-D01')
        d01.status['tasks']['shutdown']['installed'] = False
        d01.status['tasks']['shutdown']['mandatory'] = True
        self.assertFalse(d01.is_ok())
