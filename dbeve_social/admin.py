from django.contrib import admin
from django.utils.html import format_html # для экранирования опасных символов

from .models import Battlereports, Killmails, Victims

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

# class KillmailsAdmin(admin.ModelAdmin):
#     """
#     Редактор модели киллмыла
#     """
#
#     list_display = ["killmail_id", "killmail_time", "sumv" ]
#     inlines = (VictimsInliner,)
#
# class BattlereportAdmin(admin.ModelAdmin):
#     """
#     Редактор модели киллмыла
#     """
#
#     list_display = ["battlereport_id", "time_end", "kmsCount", "totalShips", "totalPilots", "url", ]

# из-за того что свзять бр-ов и киллмыл через ManyToMany, нужно сначала получить прмежуточную модель
# и указывать инлинер относительно нее. Также для значительного ускорения и чтобы избавиться от 500 ошибки
# нужно использовать autocomplete_fields - именно они требуют промежуточной модели
@admin.register(Killmails)
class KillmailsAdmin(admin.ModelAdmin):
    search_fields = ['killmail_id', 'killmail_time']  # Поля для поиска
    list_display = ['killmail_id', 'killmail_time', 'solar_system', 'link_to_zkb']
    list_filter = ['killmail_time']
    list_select_related = ['solar_system']  # Оптимизация запросов
    inlines = (VictimsInliner,)
    readonly_fields = ['link_to_zkb',]  # Добавляем кастомное поле (только для чтения)

    def link_to_zkb(self, instance):
        return format_html(
            '<a href="https://zkillboard.com/kill/{}" target="_blank">{}</a>',
            instance.killmail_id,
            instance.killmail_id
        )


class BattlereportKillmailInline(admin.TabularInline):
    model = Battlereports.killmails.through  # Используем промежуточную модель
    extra = 1
    verbose_name = "Killmail"
    verbose_name_plural = "Killmails"
    autocomplete_fields = ['killmails',]  # Указываем поле для автодополнения
    readonly_fields = ['victim_name', 'victim_ship', 'link_to_zkb',]  # Добавляем кастомное поле (только для чтения)

    def get_queryset(self, request):
        """
        переопределяем, чтобы избежать N+1
        """
        return super().get_queryset(request).prefetch_related(
            'killmails__victim__character'  # Жадно загружаем связанные данные
        )

    def victim_name(self, instance):
        """Возвращает имя персонажа из Victims или '—', если нет данных."""
        if hasattr(instance.killmails, 'victim') and instance.killmails.victim.character:
            return instance.killmails.victim.character.name
        return "---"

    def victim_ship(self, instance):
        """Возвращает тип потерянного корабля."""
        if hasattr(instance.killmails, 'victim') and instance.killmails.victim.ship:
            return instance.killmails.victim.ship.name
        return "---"

    def link_to_zkb(self, instance):
        return format_html(
            '<a href="https://zkillboard.com/kill/{}" target="_blank">{}</a>',
            instance.killmails.killmail_id,
            instance.killmails.killmail_id
        )

    victim_name.short_description = "Жертва"  # Заголовок колонки
    victim_ship.short_description = "Ship"  # Заголовок колонки
    link_to_zkb.short_description = "Zkillboard"  # Заголовок колонки

@admin.register(Battlereports)
class BattlereportAdmin(admin.ModelAdmin):
    list_display = ("battlereport_id", "time_end", "kmsCount", "totalShips", "totalPilots", "url")
    exclude = ("killmails",)  # Скрываем ManyToMany, так как используем инлайн
    inlines = [BattlereportKillmailInline]  # Подключаем инлайн

# admin.site.register(Killmails, KillmailsAdmin)
# admin.site.register(Battlereports, BattlereportAdmin)
