import sys
import pygit2
from blessed import Terminal
from pygit2 import clone_repository, GIT_SORT_REVERSE, Signature, RemoteCallbacks, UserPass
from uuid import uuid4

from input import Input
from graphics import Graphics

from typing import List

class Main():
    def __init__(self):
        self.term = Terminal()
        self.input = Input(self.term)
        self.graphics = Graphics(self.term)

        self.filler = ['~'] * (self.term.height - 1)
        self.messages = self.filler
        self.repo = None
        self.gitirc_file = None

        # TODO: Change
        self.user_name = "Kyle Sammons"
        self.user_email = "kyle.sammons@protonmail.com"

    def load_messages(self):
        self.pull(self.repo)

        if self.repo:
            loaded_messages = []
            for commit in self.repo.walk(self.repo.head.target, GIT_SORT_REVERSE):
                message = commit.message.strip()
                loaded_messages.append(f"{commit.committer.raw_name.decode()}: {message}")

            self.messages = (['~'] * ((self.term.height - 1) - len(loaded_messages))) + loaded_messages
            self.graphics.redraw(self.messages, "")

    def pull(self, repo, remote_name='origin', branch='master'):
        if not repo:
            return

        for remote in repo.remotes:
            if remote.name == remote_name:
                creds = UserPass("kyle.sammons@protonmail.com", "<BLEEP>")
                callbacks = RemoteCallbacks(credentials = creds)

                remote.fetch(callbacks=callbacks)
                remote_master_id = repo.lookup_reference('refs/remotes/origin/%s' % (branch)).target
                merge_result, _ = repo.merge_analysis(remote_master_id)
                # Up to date, do nothing
                if merge_result & pygit2.GIT_MERGE_ANALYSIS_UP_TO_DATE:
                    return
                # We can just fastforward
                elif merge_result & pygit2.GIT_MERGE_ANALYSIS_FASTFORWARD:
                    repo.checkout_tree(repo.get(remote_master_id))
                    try:
                        master_ref = repo.lookup_reference('refs/heads/%s' % (branch))
                        master_ref.set_target(remote_master_id)
                    except KeyError:
                        repo.create_branch(branch, repo.get(remote_master_id))
                    repo.head.set_target(remote_master_id)
                elif merge_result & pygit2.GIT_MERGE_ANALYSIS_NORMAL:
                    repo.merge(remote_master_id)

                    if repo.index.conflicts is not None:
                        for conflict in repo.index.conflicts:
                            print('Conflicts found in:', conflict[0].path)
                        raise AssertionError('Conflicts, ahhhhh!!')

                    user = repo.default_signature
                    tree = repo.index.write_tree()
                    commit = repo.create_commit('HEAD',
                                                user,
                                                user,
                                                'Merge!',
                                                tree,
                                                [repo.head.target, remote_master_id])
                    # We need to do this or git CLI will think we are still merging.
                    repo.state_cleanup()
                else:
                    raise AssertionError('Unknown merge analysis result')

    def send_message(self, message):
        # Make arbitrary change
        with open(self.gitirc_file, "w") as f:
            f.write(str(uuid4()))
        
        # Stage file
        index = self.repo.index
        index.add_all()
        index.write()

        # Commit
        reference = 'refs/heads/master'
        tree = index.write_tree()
        author = Signature(self.user_name, self.user_email)
        commiter = Signature(self.user_name, self.user_email)
        oid = self.repo.create_commit(reference, author, commiter, message, tree, [self.repo.head.target])

        # Setup creds?
        creds = UserPass("kyle.sammons@protonmail.com", "<BLEEP>")
        callbacks = RemoteCallbacks(credentials = creds)

        # Push

        # TODO: Get the remote for the current branch. For the moment just hardcode to origin
        remote = self.repo.remotes["origin"]
        remote.credentials = creds
        remote.push([reference], callbacks=callbacks)

    def register_server(self, trailing_words: List[str]):
        repo_name = trailing_words[0]
        repo_url = "".join(trailing_words[1:])
        repo_path = f"/tmp/gitirc/servers/{repo_name}"

        # TOOD: Don't hardcode this
        creds = UserPass("kyle.sammons@protonmail.com", "<BLEEP>")
        callbacks = RemoteCallbacks(credentials = creds)

        self.repo = clone_repository(repo_url, repo_path, callbacks=callbacks)
        self.repo.remotes.set_url("origin", repo_url)

        # Just create the file for now
        uuid = str(uuid4())
        filename = f"{repo_path}/.gitirc-{uuid}"
        with open(filename, "w"):
            self.gitirc_file = filename

        self.load_messages()

    def on_quit(self, trailing_words: List[str]):
        # TODO: Post quit message
        sys.exit(0)

    def on_input(self, buffer):
        self.graphics.redraw(self.messages, buffer)

    def start(self):
        with self.term.fullscreen(), self.term.cbreak():
            self.graphics.redraw(self.filler, "")

            self.input.on_command("quit", self.on_quit)
            self.input.on_command("server", self.register_server)
            self.input.on_input(self.on_input)
            self.input.on_enter(self.send_message)

            self.input.start_input_loop(self.load_messages)
    

if __name__ == "__main__":
    main = Main()
    main.start()
