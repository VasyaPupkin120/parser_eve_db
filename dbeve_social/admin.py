from django.contrib import admin
from django.utils.html import format_html # для экранирования опасных символов

from .models import Killmails, Victims

class VictimsInliner(admin.TabularInline):
    model = Victims
    extra = 0
    fields = ('victim_id', 'type_destroyed', 'character_link','corporation_link', 'alliance_link' )
    # нужно добавлять такие динамические поля в readonly, чтобы подхватывал именно функцию а не искал поле в модели.
    readonly_fields = ('type_destroyed', 'character_link','corporation_link', 'alliance_link' ) 

    def type_destroyed(self, obj):
        """
        можно использовать метод чтобы добавлять во первых значения из связанных записей, 
        а во вторых чтобы формировать ссылки куда нибудь.
        """
        if obj.ship:
            return format_html(
                '<a href="https://zkillboard.com/ship/{}" target="_blank">{}</a>',
                obj.ship.type_id,
                obj.ship.name
            )
        return "---"

    def character_link(self, obj):
        """
        можно использовать метод чтобы добавлять во первых значения из связанных записей, 
        а во вторых чтобы формировать ссылки куда нибудь.
        """
        if obj.character:
            return format_html(
                '<a href="https://zkillboard.com/character/{}" target="_blank">{}</a>',
                obj.character.character_id,
                obj.character.name
            )
        return "---"

    def corporation_link(self, obj):
        if obj.corporation:
            return format_html(
                '<a href="https://zkillboard.com/corporation/{}" target="_blank">{}</a>',
                obj.corporation.corporation_id,
                obj.corporation.name
            )
        return  "---"

    def alliance_link(self, obj):
        if obj.alliance:
            return format_html(
                '<a href="https://zkillboard.com/alliance/{}" target="_blank">{}</a>',
                obj.alliance.alliance_id,
                obj.alliance.name
            )
        return  "---"

    # заголовки столбцов у динамически создаваемых полей
    character_link.short_description = "Имя персонажа"
    corporation_link.short_description = "Корпорация"
    alliance_link.short_description = "Альянс"

class KillmailsAdmin(admin.ModelAdmin):
    """
    Редактор модели киллмыла
    """

    list_display = ["killmail_id", "killmail_time", "sumv" ]
    inlines = (VictimsInliner,)

admin.site.register(Killmails, KillmailsAdmin)
