from .context import scraper_context_required
from .links import CHAPTERS, obtain_tasks
from .downloader import TaskDownloader, SkipQuizTaskException

_TIMEOUT = 10
_ATTEMPTIONS_LIMIT = 5

@scraper_context_required
def scrap_chapter(chapter):
    '''
    A function is scrapping all tasks in chapter.
    '''

    print(f'{chapter}: Preparing...', end='')
    tasks = dict(obtain_tasks(CHAPTERS[chapter]))

    solved = len(tasks)
    skipped, failures = 0, 0
    for index in tasks:
        print(f'\r{chapter}: {index}/{solved} ({failures} skipped failures, {skipped} skipped quizzes)', end='')
        for attemption in range(1, _ATTEMPTIONS_LIMIT + 1):
            try:
                TaskDownloader(tasks[index], index, _TIMEOUT).download()
                break
            except SkipQuizTaskException:
                skipped += 1
                break
            except:
                if attemption == _ATTEMPTIONS_LIMIT:
                    failures += 1

    print(f'\r{chapter}: Completed                                           ')

def scrap_all():
    '''
    A function is scrapping all tasks in all chapters.
    '''

    for chapter in CHAPTERS:
        scrap_chapter(chapter)
