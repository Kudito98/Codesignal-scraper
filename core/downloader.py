import trio, json, sys, os
from queue import Queue

from .context import ScraperContext, scraper_context_required

class SkipQuizTaskException(Exception):
    '''
    This exception is raised when kind of task is quizz. 
    '''
    pass

class TaskDownloader(object):
    '''
    Class for scrapping and downloading data from task website.
    '''

    def __init__(self, link, index, timeout):
        self._link = link
        self._index = index
        self._timeout = timeout

        res = link.split('/')
        self._hash = res[-1]
        self._chapter = res[-3]

        self._text_id = None
        self._sources_id = None

        self._name = None
        self._text = None
        self._sources = None

    def _tryDump(self):
        '''
        A function checks if all data of task is collected, when the condition is true then the data is saved.
        '''

        if not self._name or not self._text or not self._sources:
            return False

        path = f'tasks/{self._chapter}/{self._index}-{self._name}'
        os.makedirs(path, exist_ok=True)

        for lang, src in self._sources:
            with open(f'{path}/{self._name}.{lang}', 'w') as f:
                f.write(src)

        with open(f'{path}/{self._name}.md', 'w') as f:
            f.write(self._text)

        return True

    async def _listening_ws_sent(self, listener):
        '''
        A function for asynchronic collecting data that was sent by Websocket.
        '''

        async for event in listener:
            payload = event.response.payload_data
            data = json.loads(payload[2:-2].replace('\\\\', '\\').replace('\\\"', '\"'))

            if data['msg'] == 'method':
                if data['method'] == 'markdownService.sanitize':
                    self._text_id = data['id']

                elif data['method'] == 'taskSolveService.getEditorState':
                    self._sources_id = data['id']

                elif data['method'] == 'quizTaskService.getOptions':
                    raise SkipQuizTaskException()

            if self._text_id and self._sources_id:
                return

    def _process_recv_msg(self, event):
        '''
        A function is processing recevied data.
        '''

        payload = event.response.payload_data
        if payload[0] != 'a':
            return False
        
        data = json.loads(payload[3:-2].replace('\\\\', '\\').replace('\\\"', '\"'))
        data_id = data.get('id', None) if data else None
        if not data_id:
            return False

        if data_id == self._hash:
            self._name = data['fields']['sourceName']

        elif data_id == self._text_id:
            self._text = data['result']

        elif data_id == self._sources_id:
            self._sources = [(file['language'], file['source']) for file in data['result']['files']]

        if self._tryDump():
            return True

    async def _listening_ws_recv(self, listener):
        '''
        A function for asynchronic collecting data that was received by Websocket.
        '''
        events = Queue()
        async for event in listener:
            events.put(event)
            if self._text_id and self._sources_id:
                break

        while not events.empty():
            if self._process_recv_msg(events.get()):
                return

        async for event in listener:
            if self._process_recv_msg(event):
                return

    async def _start(self):
        '''
        Asynchronic part of code called in function "download".
        '''

        driver = ScraperContext().driver

        async with driver.bidi_connection() as connection:
            session = connection.session
            devtools = connection.devtools

            await session.execute(devtools.network.enable())
            listener_ws_sent = session.listen(devtools.network.WebSocketFrameSent)
            listener_ws_recv = session.listen(devtools.network.WebSocketFrameReceived)
            with trio.move_on_after(self._timeout):
                async with trio.open_nursery() as nursery:
                    nursery.start_soon(self._listening_ws_sent, listener_ws_sent)
                    nursery.start_soon(self._listening_ws_recv, listener_ws_recv)
                    driver.get(self._link)

    @scraper_context_required
    def download(self):
        '''
        A function downloads tasks. 
        '''

        stderr = sys.stderr
        with open(os.devnull, 'w') as devnull:
            sys.stderr = devnull
            trio.run(self._start)

        sys.stderr = stderr
