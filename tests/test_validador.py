import sys
import types
import unittest
from unittest.mock import MagicMock, patch

_fake_symbols = types.SimpleNamespace(
    EAN13='EAN13', EAN8='EAN8', UPCA='UPCA', UPCE='UPCE',
    CODE39='CODE39', CODE93='CODE93', CODE128='CODE128',
    I25='I25', DATABAR='DATABAR', DATABAR_EXP='DATABAR_EXP',
    CODABAR='CODABAR', PDF417='PDF417', QRCODE='QRCODE'
)

pyzbar_module = types.ModuleType('pyzbar')
pyzbar_pyzbar = types.ModuleType('pyzbar.pyzbar')
pyzbar_pyzbar.ZBarSymbol = _fake_symbols
pyzbar_module.pyzbar = pyzbar_pyzbar
sys.modules.setdefault('pyzbar', pyzbar_module)
sys.modules['pyzbar.pyzbar'] = pyzbar_pyzbar

pymysql_module = types.ModuleType('pymysql')
pymysql_module.connect = lambda *args, **kwargs: None
pymysql_cursors = types.ModuleType('pymysql.cursors')
pymysql_cursors.DictCursor = object
pymysql_module.cursors = pymysql_cursors
sys.modules.setdefault('pymysql', pymysql_module)
sys.modules['pymysql.cursors'] = pymysql_cursors

from src.validador import ValidadorRegistros


class FakeBD:
    def __init__(self):
        self.operadores = {
            "G1": {
                "id_operador": 1,
                "id_maquina_asignada": 99,
                "activo": True,
            }
        }
        self.maquinas = {
            "M1": {
                "id_maquina": 7,
                "activo": True,
            }
        }
        self.registros_operador = []
        self.registros_maquina = []

    def probar_conexion(self):
        return True, "ok"

    def buscar_operador_por_gafete(self, numero_gafete):
        return self.operadores.get(numero_gafete)

    def insertar_registro_operador(self, **datos):
        self.registros_operador.append(datos)

    def buscar_maquina_por_codigo(self, codigo):
        return self.maquinas.get(codigo)

    def insertar_registro_maquina(self, **datos):
        self.registros_maquina.append(datos)


class ValidadorTests(unittest.TestCase):
    def test_debounce_respeta_cooldown(self):
        fake_bd = FakeBD()
        with patch('src.validador.BaseDatos', return_value=fake_bd):
            validador = ValidadorRegistros(MagicMock())

        with patch('src.validador.time.time', side_effect=[1.0, 1.1, 3.0]):
            self.assertFalse(validador._debounce("ABC123"))
            self.assertTrue(validador._debounce("ABC123"))
            self.assertFalse(validador._debounce("ABC123"))

    def test_toggle_operador_abre_y_cierra(self):
        fake_bd = FakeBD()
        with patch('src.validador.BaseDatos', return_value=fake_bd):
            validador = ValidadorRegistros(MagicMock())

        with patch('src.validador.MODO_REGISTRO', 'operador'), \
             patch('src.validador.time.time', side_effect=[0.0, 5.0]):
            mensaje_apertura = validador.procesar_codigo('G1', 'QRCODE')
            mensaje_cierre = validador.procesar_codigo('G1', 'QRCODE')

        self.assertIn('Apertura OPERADOR', mensaje_apertura)
        self.assertIn('Cierre OPERADOR', mensaje_cierre)
        self.assertEqual(len(fake_bd.registros_operador), 1)
        registro = fake_bd.registros_operador[0]
        self.assertEqual(registro['id_operador'], 1)
        self.assertEqual(registro['id_maquina'], 99)
        self.assertIn('inicio', registro)
        self.assertIn('fin', registro)

    def test_toggle_maquina_abre_y_cierra(self):
        fake_bd = FakeBD()
        with patch('src.validador.BaseDatos', return_value=fake_bd):
            validador = ValidadorRegistros(MagicMock())

        with patch('src.validador.MODO_REGISTRO', 'maquina'), \
             patch('src.validador.time.time', side_effect=[10.0, 15.0]):
            mensaje_apertura = validador.procesar_codigo('M1', 'CODE128')
            mensaje_cierre = validador.procesar_codigo('M1', 'CODE128')

        self.assertIn('Apertura MÁQUINA', mensaje_apertura)
        self.assertIn('Cierre MÁQUINA', mensaje_cierre)
        self.assertEqual(len(fake_bd.registros_maquina), 1)
        registro = fake_bd.registros_maquina[0]
        self.assertEqual(registro['id_maquina'], 7)
        self.assertIn('inicio', registro)
        self.assertIn('fin', registro)


if __name__ == '__main__':
    unittest.main()
