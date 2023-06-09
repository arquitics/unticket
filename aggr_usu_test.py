import time
from getpass import getpass
from login_test import login_test as login
import lib.shared_lib as shared
import utils.datetime_id as id
import traceback
import data.data_api as data_api
import random
import pandas as pd
import datetime

ROLES = ['Administrador']
USERNAMES = ['gamerboy42', 'mysticalunicorn88', 'lovetoswim99', 'hikingfanatic33', 'teadrinker12', 'familyman77', 'doglover88', 'catlady44', 'birdwatcher22', 'butterflykisses44', 'bakingqueen99', 'guitarhero55', 'pianolover77', 'saxophoneplayer11']
NOMBRES = [ 'Sofía Elena', 'Martín Andrés', 'Ana Isabel', 'Santiago Alejandro', 'Valentina Victoria' ]
APELLIDOS = [ 'García Pérez', 'Martínez Sánchez', 'Ramírez González', 'Gómez Rodríguez', 'Castro Ruiz' ]
TIPOSDOC = ['T.I.', 'C.C.', 'Pasaporte', 'Cédula de Extranjería']
NUMSDOC = ['67890123', 'FG789012', '1234567A', '4567890B', '8901234C', '2345678D', '5678901E', '9012345F', 'CD567890', 'EF789012', 'GH901234', 'IJ345678', 'KL901234']
ROLES_2 = ['Administrador', 'Gestor 1', 'Gestor 2', 'Recepción', 'Solicitante']

def aggr_usu_test(driver, DF, caso, rol, username, nombres, apellidos, tipo_doc, num_doc, roles):

    UAC = 3
    passed = 0

    FUNC_STR = 'Agregar Usuario'
    PARAMS_STR = f'Nombres: {nombres}\nApellidos: {apellidos}\nTipo Doc: {tipo_doc}\nNum Doc: {num_doc}\nRoles: {roles}'

    try:

        shared.select_role(driver, rol)
        time.sleep(5)

        shared.select_module(driver, 'Administrar usuarios')
        time.sleep(2)
        shared.click_button(driver, 'Agregar')
        time.sleep(2)
        shared.enter_input_value(driver, 'Username', username)
        shared.enter_input_value(driver, 'Nombres', nombres)
        shared.enter_input_value(driver, 'Apellidos', apellidos)
        shared.select_value(driver, 'Tipo de documento', tipo_doc)
        shared.enter_input_value(driver, 'Documento', num_doc)
        shared.multiselect_values(driver, 'Roles', roles)
        shared.press_esc_key(driver)
        shared.click_button(driver, 'Guardar')
        time.sleep(5)

        # [UAC] El rol seleccionado se mantiene tras enviar el formulario
        result = shared.UAC_compare_form_fields([shared.get_role(driver)], [rol])
        passed += shared.evaluate_UAC_result(result)
        DF = data_api.write_row_to_df(DF, caso, FUNC_STR, rol, PARAMS_STR,
                                 'El rol seleccionado se mantiene tras enviar el formulario', 
                                 f"{'SI' if result[0] else 'NO'} : {result[1]}",
                                 'PASSED' if result[0] else 'FAILED')
        # END UAC CHECK

        # [UAC] El usuario se guarda con los datos correctos
        shared.search(driver, 'Usuarios', username)
        time.sleep(3)
        result = shared.UAC_validate_saved_record(driver, 'Usuarios', [username, ' '.join(roles)], 0)
        passed += shared.evaluate_UAC_result(result)
        DF = data_api.write_row_to_df(DF, caso, FUNC_STR, rol, PARAMS_STR,
                                 'El usuario se guarda con los datos correctos', 
                                 f"{'SI' if result[0] else 'NO'} : {result[1]}",
                                 'PASSED' if result[0] else 'FAILED')
        # END UAC CHECK

        time.sleep(2)

        # [UAC] Los datos del usuario aparecen correctamente en el modo edición
        shared.click_edit_button(driver, 'Usuarios', 0, pos=0)   
        result = shared.UAC_compare_form_fields([shared.get_input_value(driver, 'Username'),
                                                shared.get_input_value(driver, 'Nombres'),
                                                shared.get_input_value(driver, 'Apellidos'),
                                                shared.get_input_value(driver, 'Tipo de documento'),
                                                shared.get_input_value(driver, 'Documento'),
                                                shared.get_checkbox_value(driver, 'Estado'),
                                                sorted(shared.get_multiselect_values(driver, 'Roles'))
                                                ], [username, nombres, apellidos, tipo_doc, num_doc, True, sorted(roles)])
        passed += shared.evaluate_UAC_result(result)
        shared.click_button(driver, 'Cerrar', 1)
        DF = data_api.write_row_to_df(DF, caso, FUNC_STR, rol, PARAMS_STR,
                                 'Los datos del usuario aparecen correctamente en el modo edición', 
                                 f"{'SI' if result[0] else 'NO'} : {result[1]}",
                                 'PASSED' if result[0] else 'FAILED')
        # END UAC CHECK

        print(f'AGGR USU: {passed}/{UAC} UAC PASSED')

        return DF

    except Exception as e:
        traceback.print_exc()
        DF = data_api.write_row_to_df(DF, caso, FUNC_STR, rol, PARAMS_STR, 'EXCEPTION', e, 'EXCEPTION')
        print(f'AGGR USU: {passed}/{UAC} UAC PASSED')
        return DF

if __name__ == "__main__":

    DF = pd.DataFrame(columns=['CASO', 'FUNCIONALIDAD', 'ROL', 'PARAMS', 'UAC', 'SALIDA', 'RESULTADO'])

    driver = shared.init_driver()
    login(driver, input('Username: '), getpass('Password: '))

    start_time = time.time()
    total_time = 0

    nexp = 10
    wait = 19

    for i in range(nexp):

        rol = random.choice(ROLES)
        username = f'{USERNAMES[i]} - {id.get_id_()}'
        nombres = random.choice(NOMBRES)
        apellidos = random.choice(APELLIDOS)
        tipo_doc = random.choice(TIPOSDOC)
        num_doc = f'{NUMSDOC[i]} - {id.get_id_()}'
        roles = random.sample(ROLES_2, random.randint(1, len(ROLES_2)))

        DF = aggr_usu_test(driver, DF, caso=i+1, rol=rol, username=username, nombres=nombres, apellidos=apellidos, tipo_doc=tipo_doc, num_doc=num_doc, roles=roles)

        iteration_time = time.time() - start_time - total_time
        total_time += iteration_time

        print(f"Caso {i+1} tomó: {datetime.timedelta(seconds=iteration_time)}")
        print(f"Caso {i+1} sin espera tomó aprox.: {datetime.timedelta(seconds=iteration_time - wait)}")

    avg_time_per_iteration = total_time / nexp
    total_time = time.time() - start_time

    print('\n\n\n')
    print(f"Tiempo promedio por caso: {datetime.timedelta(seconds=avg_time_per_iteration)}")
    print(f"Tiempo promedio aprox. por caso sin espera: {datetime.timedelta(seconds=avg_time_per_iteration - wait)}") 
    print(f"Tiempo total para {nexp} casos: {datetime.timedelta(seconds=total_time)}")
    print(f"Tiempo total aprox. para {nexp} casos sin espera: {datetime.timedelta(seconds=total_time - wait * nexp)}")

    DF.to_excel(r'results\aggr_usu_test_results.xlsx', index=False)


    
    