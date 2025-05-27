###############################################################################
#                           Загрузка изображения.                             #
###############################################################################


# def load_and_save_icon(entity: Literal["alliance", "corporation", "character"], entity_id):
#     """
#     получает название сущности (alliance, corporation, char), id сущности, 
#     загружается изображение 128х128 (оно вроде есть и у чаров
#     и у корпораций и у алли). 
#
#     Возвращает имя файла изображения (нужно для загрузки из статических файлов,
#     т.к. заранее неизвестно какое расширение), его нужно сохранять в модель альянса,
#     корпорации и т.д.
#
#     Расширение (jpeg, png) определяется на основе заголовков ответа.
#
#     Нужно помнить, что парсинг изображений идет не с esi а с некоего файлового
#     сервера, поэтому нужно как то поаккуратней, там могут быть другие лимиты запросов
#     и могут блочить парсинг изображений.
#     """
#
#     if entity == "alliance":
#         url_images = f"https://images.evetech.net/Alliance/{entity_id}_128.png"
#         path = settings.STATICFILES_DIRS[0].joinpath("img/alliances")
#     elif entity == "corporation":
#         url_images = f"https://images.evetech.net/corporations/{entity_id}/logo?tenant=tranquility&size=128"
#         path = settings.STATICFILES_DIRS[0].joinpath("img/corporations")
#     elif entity == "character":
#         url_images = f"https://images.evetech.net/characters/{entity_id}/portrait?tenant=tranquility&size=128"
#         path = settings.STATICFILES_DIRS[0].joinpath("img/characters")
#     else:
#         raise_entity_not_processed(entity)
#
#     # пробуем использовать ту же функцию загрузки, что и все esi-запросы
#     # несмотря на то, что это запрос не к esi а к images.evetech.net
#     # в приципе запросы к esi занимают 300-400 мс
#     # и на одну сущность - только один запрос изображения,
#     # поэтому не буду ставить какие то временные задержки запросов изображений.
#     # посмотрим, не будут ли блочить.
#     print("start load image")
#     resp = GET_request_to_esi(url_images)
#     print("succeful load image")
#
#     file_extension = resp.headers["Content-Type"].split("/")[-1]
#     filename = f"{entity_id}_128.{file_extension}"
#     full_filename = path.joinpath(filename)
#
#     print(f"start save image to {full_filename}")
#     with open(full_filename, "wb") as file:
#         file.write(resp.content)
#     print("succeful save image")
#
#     return filename
#
#
#
#
