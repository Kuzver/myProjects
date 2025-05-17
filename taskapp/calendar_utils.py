# calendar_utils.py
import calendar

class BootstrapCalendar(calendar.HTMLCalendar):
    def formatday(self, day, weekday):
        if day == 0:
            return '<td class="bg-light"></td>'  # Пустая ячейка (нет дня)
        return f'<td class="text-center">{day}</td>'

    def formatweek(self, theweek):
        return '<tr>' + ''.join(self.formatday(d, wd) for d, wd in theweek) + '</tr>'

    def formatmonth(self, theyear, themonth, withyear=True):
        weeks = self.monthdays2calendar(theyear, themonth)
        s = '<table class="table table-bordered table-striped">\n'

        header_days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        header_html = ''.join(f'<th class="text-center">{day}</th>' for day in header_days)
        s += f'<thead><tr>{header_html}</tr></thead>\n'

        s += '<tbody>\n'
        for week in weeks:
            s += self.formatweek(week) + '\n'
        s += '</tbody></table>'
        return s
