#!/usr/bin/env python3

import argparse, code
import core as scraper

parser = argparse.ArgumentParser(description='The Scraper for CodeSignal')

manual = parser.add_argument_group('manual mode')
manual.add_argument('-m', dest='manual', action='store_true')

chapter = parser.add_argument_group('scraper options')
chapter.add_argument('chapter', metavar='CHAPTER', type=str, nargs='?')
chapter.add_argument('-t', dest='tasks', metavar='TASK', type=str, nargs='+')
chapter.set_defaults(chapter='all')

args = parser.parse_args()
with scraper.ScraperContext():
    if args.manual:
        local = {name: eval(f'scraper.{name}') for name in scraper.__all__}
        local['scraper'] = scraper
        code.interact(local=local)

    elif args.chapter == 'all':
        scraper.scrap_all()

    elif not args.tasks:
        scraper.scrap_chapter(args.chapter)

    else:
        print(f'{args.chapter}: preparing...')
        chapter_url = scraper.CHAPTERS[args.chapter]
        links = {index: link for index, link in scraper.obtain_tasks(chapter_url) if index in args.tasks}

        for index in links:
            print(f'{args.chapter}: scrap task: {index}', end='')
            for attemption in range(1, 6):
                try:
                    scraper.TaskDownloader(links[index], index, 10).download()
                    break

                except scraper.SkipQuizTaskException:
                    print(f'\r{args.chapter}: scrap task: {index} (skipped quiz)', end='')
                    break

                except:
                    print(f'\r{args.chapter}: scrap task: {index} ({attemption} failures)', end='')

            print('')
