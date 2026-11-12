'''
Скрипт проверки данных из пдф на соответствие шаблону и нормам
check_hourstables_one - Проверка одной формы обучения в документе (в док. только очно/заочно) - сверка часов из таблиц
check_hourstables_all - Проверка всех форм обученияв документе в док.  очно или заочно) - сверка часов из таблиц
chek_headers - сверка заголовков 
chek_comp - проверка компетенций - сверяем, что ОПК есть в БД
check_hours - проверяет зачетные единицы
'''
from pdf_extractor import get_pdf_headers, get_pdf_tables,get_themes,get_main_literature,get_additional_literature,get_learning_form
from db.cruid import get_required_headers, get_competentions
import re
def check_hourtables(pdf_path):
    if get_learning_form(pdf_path) == "solo":
        return check_hourstables_one(pdf_path)
    else: 
        return check_hourstables_all(pdf_path)

def check_themes(pdf_path):
    if get_learning_form(pdf_path) == "solo":
        return check_themes_one(pdf_path)
    else: 
        return check_themes_all(pdf_path)

def check_hourstables_one(pdf_path):
    '''
    сверяет часы из таблиц (2 таблицы)
    '''
    errs =[]
    result = True
    if pdf_path:
        tables = get_pdf_tables(pdf_path)
        total_hours = 0

        #первая таблица - трудоемкость
        for i in range (len(tables[1])-1):
            if tables[1][i][0]:
                if tables[1][i][0].replace(",","").isdigit():
                    if tables[1][i][2] and tables[1][i][2].replace(",","").isdigit():
                        total_hours += float(tables[1][i][2].replace(",","."))
        if total_hours != float(tables[1][len(tables[1])-1][2].replace(",",".")):
            result = False
            errs.append(f"Часы в таблице трудоескости не сходятся {total_hours} и {float(tables[1][len(tables[1])-1][2].replace(",","."))}")
        
        
        total_hours = 0
        #вторая таблица - план изучения
        for k in range(len(tables[2])-1):
            row_total = 0
            for i in range (3,len(tables[2][k])):
                if tables[2][k][i]:
                    if tables[2][k][i].replace(",","").isdigit():
                        row_total+=float(tables[2][k][i].replace(",","."))
            if tables[2][k][2]:
                if tables[2][k][2].replace(",","").isdigit():
                    if row_total != float(tables[2][k][2].replace(",",".")):
                        return(False,"hours dont match, table 3 (row)")
            total_hours += row_total
        if not tables[2][len(tables[2])-1][2]:
            return (False, "ошибка в формате таблицы")
        if total_hours != float(tables[2][len(tables[2])-1][2].replace(",",".")):
            result = False
            errs.append(f"Часы в таблице плана изучения не сходятся - {total_hours} и {float(tables[2][len(tables[2])-1][2].replace(",","."))}")
        return (result,errs)
    return (False, "path is not defined")

def check_hourstables_all(pdf_path):
    '''
    сверяет часы из таблиц (4 таблицы)
    '''
    if pdf_path:
        tables = get_pdf_tables(pdf_path)
        errs=[]
        result = True
        total_hours = 0
        total_hours_lection_first = 0
        total_hours_lection_second = 0
        total_hours_semi_first=0
        total_hours_semi_second=0
        total_hours_lab_first=0
        total_hours_lab_second=0
        total_hours_pract_first=0
        total_hours_pract_second=0
        total_hours_self_first=0
        total_hours_self_second=0
        
        #первая таблица - трудоемкость
        for i in range (len(tables[1])-1):
            if tables[1][i][0]:
                if tables[1][i][0].replace(",","").isdigit():
                    if tables[1][i][2] and tables[1][i][2].replace(",","").isdigit():
                        total_hours += float(tables[1][i][2].replace(",","."))
                if tables[1][i][1] == "Лекции" and tables[1][i][2]:
                    total_hours_lection_first = float(tables[1][i][2].replace(",","."))
                elif tables[1][i][1] == "Семинарские/практические занятия" and tables[1][i][2]:
                    total_hours_semi_first=float(tables[1][i][2].replace(",","."))
                elif tables[1][i][1] == "Лабораторные занятия" and tables[1][i][2]:
                    total_hours_lab_first=float(tables[1][i][2].replace(",","."))
                elif tables[1][i][1] == "Практическая подготовка" and tables[1][i][2]:
                    total_hours_pract_first = float(tables[1][i][2].replace(",","."))
                elif tables[1][i][1] == "Самостоятельная работа" and tables[1][i][2]:
                    total_hours_self_first = float(tables[1][i][2].replace(",","."))
        if total_hours != float(tables[1][len(tables[1])-1][2].replace(",",".")):
            result = False
            errs.append(f"Часы в первой таблице трудоескости не сходятся - {total_hours} и {float(tables[1][len(tables[1])-1][2].replace(",","."))}")
        
    
        total_hours = 0
        
        #вторая таблица - трудоемкость
        for i in range (len(tables[2])-1):
            if tables[2][i][0]:
                if tables[2][i][0].replace(",","").isdigit():
                    if tables[2][i][2] and tables[1][i][2].replace(",","").isdigit():
                        total_hours += float(tables[2][i][2].replace(",","."))
                if tables[2][i][1] == "Лекции" and tables[2][i][2]:
                    total_hours_lection_second = float(tables[2][i][2].replace(",","."))
                elif tables[2][i][1] == "Семинарские/практические занятия" and tables[2][i][2]:
                    total_hours_semi_second=float(tables[2][i][2].replace(",","."))
                elif tables[2][i][1] == "Лабораторные занятия" and tables[2][i][2]:
                    total_hours_lab_second=float(tables[2][i][2].replace(",","."))
                elif tables[1][i][1] == "Практическая подготовка" and tables[1][i][2]:
                    total_hours_pract_second = float(tables[1][i][2].replace(",","."))
                elif tables[2][i][1] == "Самостоятельная работа" and tables[2][i][2]:
                    total_hours_self_second = float(tables[2][i][2].replace(",","."))

        if total_hours != float(tables[2][len(tables[2])-1][2].replace(",",".")):
            result = False
            errs.append(f"Часы во второй таблице трудоескости не сходятся - {total_hours} и {float(tables[1][len(tables[1])-1][2].replace(",","."))}")
        
        

        total_hours = 0
        lect_total = 0
        semi_total=0
        labs_total=0
        pract_total=0
        self_total = 0
        
        #третья таблица - план изучения
        for k in range(2,len(tables[3])-1):
            row_total = 0
            
            #проверка суммы в ряде
            for i in range (3,len(tables[3][k])):
                if tables[3][k][i]:
                    if tables[3][k][i].replace(",","").isdigit():
                        
                        row_total+=float(tables[3][k][i].replace(",","."))

            #Проверки часов с таблицей трудоемкости - сохранение общего числа
            if tables[3][k][3]:
                if tables[3][k][3].replace(",","").isdigit():
                    lect_total+=float(tables[3][k][3].replace(",","."))
            if tables[3][k][4]:
                if tables[3][k][4].replace(",","").isdigit():
                    semi_total+=float(tables[3][k][4].replace(",","."))
  
            if tables[3][k][5]:
                if tables[3][k][5].replace(",","").isdigit():
                    labs_total+=float(tables[3][k][5].replace(",","."))
   
            if tables[3][k][6]:
                if tables[3][k][6].replace(",","").isdigit():
                    pract_total+=float(tables[3][k][6].replace(",","."))

            if tables[3][k][7]:
                if tables[3][k][7].replace(",","").isdigit():
                    self_total+=float(tables[3][k][7].replace(",","."))


            if tables[3][k][2]:
                if tables[3][k][2].replace(",","").isdigit():
                    if row_total != float(tables[3][k][2].replace(",",".")):
                        result = False
                        errs.append(f"Часы в первой таблице плана изучения не сходятся в ряду №{k}")
                    
            total_hours += row_total
        #проверка общей суммы

        if total_hours != float(tables[3][len(tables[3])-1][2].replace(",","")):
            result = False
            errs.append(f"Общее количество часов в первой таблице плана изучения не сходятся - {total_hours} и {float(tables[3][len(tables[3])-1][2].replace(",",""))}")
        
        #проверка совпадения часов
        if semi_total != total_hours_semi_first:
            result = False
            errs.append(f"В очной форме не совпадают часы семинаров: должно быть: {total_hours_semi_first}, на самом деле: {semi_total}")
        if lect_total != total_hours_lection_first:
            result = False
            errs.append(f"В очной форме не совпадают часы лекций: должно быть: {total_hours_lection_first}, на самом деле: {lect_total}")
        if labs_total != total_hours_lab_first:
            result = False
            errs.append(f"В очной форме не совпадают часы лабораторных: должно быть: {total_hours_lab_first}, на самом деле: {labs_total}")
        if pract_total != total_hours_pract_first:
            result = False
            errs.append(f"В очной форме не совпадают часы практических: должно быть: {total_hours_pract_first}, на самом деле: {pract_total}")
        if self_total != total_hours_self_first:
            result = False
            errs.append(f"В очной форме не совпадают часы самостоятельной работы: должно быть: {total_hours_self_first}, на самом деле: {self_total}")

        
        total_hours = 0
        lect_total = 0
        semi_total=0
        labs_total=0
        pract_total=0
        self_total = 0

        total_hours = 0
        
        #четвертая таблица - план изучения
        for k in range(2,len(tables[4])-1):
            row_total = 0
            for i in range (3,len(tables[4][k])):
                if tables[4][k][i]:
                    if tables[4][k][i].replace(",","").isdigit():
                        row_total+=float(tables[4][k][i].replace(",","."))

             #Проверки часов с таблицей трудоемкости - сохранение общего числа
            if tables[4][k][3]:
                if tables[4][k][3].replace(",","").isdigit():
                    lect_total+=float(tables[4][k][3].replace(",","."))
            if tables[4][k][4]:
                if tables[4][k][4].replace(",","").isdigit():
                    semi_total+=float(tables[4][k][4].replace(",","."))
            if tables[4][k][5]:
                if tables[4][k][5].replace(",","").isdigit():
                    labs_total+=float(tables[4][k][5].replace(",","."))
            if tables[4][k][6]:
                if tables[4][k][6].replace(",","").isdigit():
                    pract_total+=float(tables[4][k][6].replace(",","."))
            if tables[4][k][7]:
                if tables[4][k][7].replace(",","").isdigit():
                    self_total+=float(tables[4][k][7].replace(",","."))



            if tables[4][k][2]:
                if tables[4][k][2].replace(",","").isdigit():
                    if row_total != float(tables[4][k][2].replace(",",".")):
                        result = False
                        errs.append(f"Часы во второй таблице плана изучения не сходятся в ряду №{k}")
            total_hours += row_total
        if total_hours != float(tables[4][len(tables[4])-1][2].replace(",","")):
            result = False
            errs.append(f"Общее количество часов во второй таблице плана изучения не сходятся - {total_hours} и {float(tables[3][len(tables[3])-1][2].replace(",",""))}")
        
        #проверка совпадения часов
        if semi_total != total_hours_semi_second:
            result = False
            errs.append(f"В заочной форме не совпадают часы семинаров: должно быть: {total_hours_semi_second}, на самом деле: {semi_total}")
        if lect_total != total_hours_lection_second:
            result = False
            errs.append(f"В заочной форме не совпадают часы лекций: должно быть: {total_hours_lection_second}, на самом деле: {lect_total}")
        if labs_total != total_hours_lab_second:
            result = False
            errs.append(f"В заочной форме не совпадают часы лабораторных: должно быть: {total_hours_pract_second}, на самом деле: {labs_total}")
        if pract_total != total_hours_pract_second:
            result = False
            errs.append(f"В заочной форме не совпадают часы практических: должно быть: {total_hours_self_second}, на самом деле: {pract_total}")
        if self_total != total_hours_self_second:
            result = False
            errs.append(f"В заочной форме не совпадают часы самостоятельной работы: должно быть: {total_hours_self_second}, на самом деле: {self_total}")

        return (result, errs)
    return (False, "файл отсутствует")

def chek_headers(pdf_path):
    '''
    Проверяет, чтобы все необходимые части были в PDF
    '''
    if pdf_path:
        missing_headers = []
        headers = get_pdf_headers(pdf_path)
        required_headers = get_required_headers()
        for header in required_headers:
            if header not in headers:
                print(header)
                missing_headers.append(header)
        if not missing_headers:
            return (True,"")
        return (False, missing_headers)
    return (False, "файл отсутствует")

def check_comp(pdf_path):
    '''
    сверяет, чтобы компетенции были правильно обозначены
    '''
    if pdf_path:
        wrong_competentions = []
        competentions = get_competentions()
        tables = get_pdf_tables(pdf_path)
        for i in (1,len(tables[0])-1):
            if tables[0][i][0]:
                if tables[0][i][0][0]=='О':
                    if tables[0][i][0] not in competentions:
                        wrong_competentions.append(tables[0][i][0])

        
        if not wrong_competentions:
            return (True,"")
        return (False, wrong_competentions)
    return (False, "файл отсутствует")

def check_themes_one(pdf_path):
    '''
    сверяет, чтобы все темы были расписаны для одной формы обучения
    '''
    req_themes = []
    tables = get_pdf_tables(pdf_path)
    temp =  get_themes(pdf_path)
    errs=[]
    if temp[0]:
        text = temp[1]
        found_themes=0
        for row in tables[2]:
            if "." in row[0]:
                req_themes.append(row[1].replace("\n"," "))
        for theme in req_themes:
            if theme in text:
                found_themes+=1
            else: errs.append(theme)
        if found_themes == len(req_themes):
            return (True,"")
        return(False,errs)
    return(False,"не найден раздел содержания дисциплины")

def check_themes_all(pdf_path):
    '''
    сверяет, чтобы все темы были расписаны для двух форм обучения
    '''
    tables = get_pdf_tables(pdf_path)
    result = True
    req_themes_och = []
    req_themes_zaoch=[]
    temp =  get_themes(pdf_path)
    errs=[]
    if temp[0]:
        text = temp[1]
        found_themes=0
        for row in tables[3]:
            if row[0]:
                if "." in row[0]:
                    req_themes_och.append(row[1].replace("\n"," "))
        for row in tables[4]:
            if row[0]:
                if "." in row[0] and row[0]:
                    req_themes_zaoch.append(row[1].replace("\n"," "))
        if req_themes_och !=req_themes_zaoch:
            result = False
            errs.append("темы для двух форм обучения не совпадают")
        for theme in req_themes_och:
            if theme in text:
                found_themes+=1
            else: errs.append(theme)
        if found_themes == len(req_themes_och):
            return (result,errs)
        return(False,errs)
    return(False,"не найден раздел содержания дисциплины")

def check_literature(pdf_path):
    main_literature = get_main_literature(pdf_path)
    additional_literature = get_additional_literature(pdf_path)
    result=True
    errs=[]
    if main_literature:
        i = 0
        for literature in main_literature:
            i+=1
            if literature[0] != str(i):
                result = False
                errs.append(f"в следующем источнике неправильный порядковый номер - {literature}")
            year = re.search(r'\d+\d+\d+\d+',literature)
            #основная литература не старше 5 лет
            if year:
                if 2026-int(year.group()) >5:
                    result = False
                    errs.append(f"Источник старше необходимого возраста (5 лет) - {literature}")
            else: 
                result = False
                errs.append(f"в следующем источнике не обнаружен год - {literature}")
    else:
        result = False
        errs.append("Не обнаружена основная литература")
    if additional_literature:
        i=0
        for literature in additional_literature:
            i+=1
            if literature[0] != str(i):
                result = False
                errs.append(f"в следующем источнике неправильный порядковый номер - {literature}")
            year = re.search(r'\d+\d+\d+\d+',literature)
            #дополнительная литература не старше 10 лет
            if year:
                if 2026-int(year.group()) >10:
                    result = False
                    errs.append(f"Источник старше необходимого возраста (10 лет) - {literature}")
            else: 
                result = False
                errs.append(f"в следующем источнике не обнаружен год - {literature}")
    else:
        result = False
        errs.append("Не обнаружена дополнительная литература")
    return(result,errs)
if __name__ == "__main__":
    pdf_file = "RPD_test2.pdf"  
    
    try:
        #print(check_hourstables_one(pdf_file))
        print(check_hourstables_all(pdf_file))
        print(chek_headers(pdf_file))
        print(check_comp(pdf_file))
        print(check_themes_all(pdf_file))
        print(check_literature(pdf_file))
    except FileNotFoundError:
        print(f"Ошибка: Файл '{pdf_file}' не найден")
        print("Укажите правильный путь к PDF файлу")
    except Exception as e:
        print(f"Ошибка: {e}")
    