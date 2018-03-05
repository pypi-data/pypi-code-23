import time
from pathlib import Path
import subprocess
import tempfile

import click
from google_auth_oauthlib.flow import InstalledAppFlow

from .context import Context, Run
from .config import DEFAULT_CONFIG_FILENAME
from .utils import find_in_ancestor
from . import judge, cli


@click.group()
@click.option('-c', '--config', type=click.Path(
    dir_okay=False,
    exists=True,
    readable=True,
    resolve_path=True,
))
@click.pass_context
def main(ctx, config):
    if config:
        config = Path(config)
        root = config.parent
        config_filename = config.name
        assert config.exists()
    else:
        path = Path('.').resolve()
        try:
            root = find_in_ancestor(path, DEFAULT_CONFIG_FILENAME)
        except ValueError:
            root = path
        config_filename = DEFAULT_CONFIG_FILENAME

    ctx.obj = Context(root=root, config_filename=config_filename)


@main.command()
@click.pass_obj
def login(context):
    client_id = context.get_password('app-client-id')
    new_client_id = click.prompt(
        'Google Application Client ID',
        default=client_id,
        show_default=bool(client_id),
    )

    client_secret = context.get_password('app-client-secret')
    if not client_secret or new_client_id != client_id:
        client_secret = click.prompt(
            'Google Application Client Secret',
            hide_input=True, confirmation_prompt=True,
        )
    client_id = new_client_id

    flow = InstalledAppFlow.from_client_config(
        judge.get_client_config(client_id, client_secret),
        scopes=['https://www.googleapis.com/auth/userinfo.email'],
    )
    credentials = flow.run_console()

    context.set_password('app-client-id', client_id)
    context.set_password('app-client-secret', client_secret)
    context.set_password(
        context.config.judge_username,
        judge.serialize_credentials(credentials),
    )


@main.command()
@click.pass_obj
def whoami(context):
    def print_attrs(container, attrs):
        for key, label in attrs.items():
            val = click.style(str(getattr(container, key)), fg="yellow")
            click.echo(f'{label:<12s}: {val}')

    account = context.judge.whoami()

    click.echo('ACCOUNT')
    print_attrs(account, {
        'id': 'ID',
        'display_name': 'Name',
        'email': 'E-mail',
        'country': 'Country',
    })

    click.echo()
    click.echo('TEAM')
    print_attrs(account.team, {
        'id': 'ID',
        'name': 'Name',
        'finalist': 'Is finalist',
    })


@main.command()
@click.pass_obj
def rounds(context):
    for round in context.judge.rounds():
        name = click.style(
            round.name,
            fg='green' if round.is_open() else 'red'
        )
        click.echo(f' * {name} ({round.start} - {round.end})')
        for ds in round.data_sets:
            click.echo(f'   * {ds.name}')


def download_assets(context):
    with cli.spinner('Download problem statement') as s:
        statement_path = context.root / context.config.statement_path
        statement_path.parent.mkdir(exist_ok=True, parents=True)

        if not context.round.is_open():
            s.skip()

        cli.download_progress(
            context.round.request_statement(),
            statement_path,
        )

    with cli.spinner('Download datasets') as s:
        datasets_dir = context.root / context.config.datasets_path
        datasets_dir.mkdir(exist_ok=True, parents=True)

        if not context.round.is_open():
            s.skip()

        for ds in context.round.data_sets:
            s.text = f'Downloading "{ds.name}"...'
            context.data.setdefault('datasets', {})[ds.slug] = ds.id
            cli.download_progress(
                ds.request_input(),
                (datasets_dir / ds.slug).with_suffix('.in'),
            )
        s.text = f'Download datasets ({len(context.round.data_sets)})'


@main.command()
@click.option('-f', '--force', is_flag=True)
@click.argument('directory', default='.',
                type=click.Path(file_okay=False, resolve_path=True))
@click.pass_context
def init(click_context, force, directory):
    root = Path(directory)

    if not force and root.exists() and root.iterdir():
        raise click.UsageError(
            f'The directory {root} is not empty.\nUse -f/--force to force the '
            f'initialization (some files may be overwritten).'
        )

    click_context.obj = context = Context.init(root=root)

    # Get round to initialize
    rounds = context.judge.rounds()
    click.echo()
    for i, round in enumerate(rounds):
        click.echo(f' [{i+1}] {round.name}')
    click.echo()

    while True:
        round_id = click.prompt(f'Select a round to setup [1-{i+1}]')
        try:
            round_id = int(round_id) - 1
        except ValueError:
            continue
        if 0 <= round_id < len(rounds):
            round = rounds[round_id]
            break

    click.echo()

    if not round.is_open():
        click.secho(
            'This round is not open, downloads will be skipped.',
            fg='yellow',
        )
        click.echo()

    with cli.spinner('Write data file'):
        context.data = {
            'round_id': round.id,
            'highscores': {},
            'datasets': {},
        }
        context.persist_data()

    download_assets(context)

    with cli.spinner('Prepare code repository'):
        code_path = context.root / context.config.code_path
        subprocess.check_output(['git', 'init', str(code_path)])

    with cli.spinner('Initialize remaining directory structure'):
        runs_dir = context.root / context.config.runs_path
        runs_dir.parent.mkdir(exist_ok=True, parents=True)

    click.secho('\nAll done, good luck!', fg='yellow')


@main.command()
@click.pass_obj
def get(context):
    if not context.round.is_open():
        click.secho(
            'This round is not open, cannot download assets.',
            fg='red',
        )
    else:
        download_assets(context)
        context.persist_data()


@main.command()
@click.argument('dataset_slug')
@click.pass_obj
def exec(context, dataset_slug):
    for dataset in context.datasets:
        if dataset.stem.startswith(dataset_slug):
            break
    else:
        raise click.UsageError('Dataset "{dataset_slug}" not found.')

    with tempfile.TemporaryDirectory() as tempdir:
        tempdir = Path(tempdir)
        run = Run(context, tempdir)
        result = run.run_dataset(dataset, capture_output=False)

        click.echo()
        click.echo(f'Reported score: {result.score}')


@main.command()
@click.option('-s', '--submit/--no-submit')
@click.option('-o', '--only', multiple=True)
@click.pass_obj
def run(context, submit, only):
    # TODO: Instead of archiving the code:
    # - git-commit everything
    # - git-tag with run?
    # - submit the git-archive?
    # - git push?

    current_highscore = context.highscore

    run = context.init_next_run()

    label = click.style(f'{run.id}', fg='yellow')
    click.echo(f'Starting run {label}')
    click.echo()

    # Archive code
    with cli.spinner('Create source code archive'):
        run.archive_code()

    # Run code
    results = []

    datasets = context.datasets
    if only:
        datasets = [datasets[int(i)] for i in only]

    for dataset in datasets:
        click.echo()
        with cli.timed_spinner(f'Run {dataset.stem}') as s:
            result = run.run_dataset(dataset)

            if result.interrupted():
                s.skip('interrupted')
            elif result.failed():
                s.fail()

        if result.interrupted():
            continue
        elif result.succeeded():
            highscore = context.dataset_highscore(dataset)
            if not highscore or result > highscore:
                # Register new highscore
                context.register_highscore(result)

            if not highscore:
                # First result
                click.secho(f'  First score: {result.score:,d}', fg='green')
            elif result > highscore:
                # New highscore
                diff = result.score - highscore.score
                percent = diff / highscore.score
                click.secho((
                    f'  New high score: {result.score:,d} '
                    f'(+{diff:,d} / +{percent:.2%} from {highscore.score:,d})'
                ), fg='green')
            elif result.score < highscore.score:
                # Worse result than previous highscore
                current = click.style(
                    f'(current HS: {highscore.score:,d})',
                    fg='cyan',
                )
                click.echo(f'  Score: {result.score:,d} {current}')
            else:
                # Same result as previous highscore
                click.echo(f'  Score: {result.score:,d}')

            results.append(result)
        else:
            err_log = click.style(str(result.error_log_path), fg='red')
            click.secho(f'  Error log stored in {err_log}')

    total_score = sum((r.score for r in results), 0)
    new_highscore = context.highscore

    run.persist_data(results)
    context.persist_data()

    click.echo()
    click.echo(f'Total score: {total_score:,d}')
    if current_highscore and new_highscore > current_highscore:
        diff = new_highscore - current_highscore
        percent = diff / current_highscore
        click.secho((
            f'New high score: {new_highscore:,d} '
            f'(+{diff:,d} / +{percent:.2%} from {current_highscore:,d})'
        ), fg='green')
    click.echo()

    # Submit solution
    if submit:
        click.get_current_context().invoke(submit_solutions)


@main.command(name='submit')
@click.pass_obj
@click.argument('run', required=False)
def submit_solutions(context, run):
    # TODO: Submit combination of best results
    # TODO: Allow to specify single dataset

    if run == 'best':
        highscores = (
            context.dataset_highscore(dataset)
            for dataset in context.datasets
        )
        datasets = [
            (hs.run, hs.dataset)
            for hs in highscores if hs is not None
        ]
    elif run and run != 'last':
        run = context.get_run(run)
        datasets = [
            (run, dataset)
            for dataset in context.datasets
        ]
    else:
        run = context.last_run()
        datasets = [
            (run, dataset)
            for dataset in context.datasets
        ]

    round = context.round

    sources_blob_keys = {}
    submissions = {}
    results = {}

    for run, dataset in datasets:
        if run not in sources_blob_keys:
            with cli.spinner(f'Upload source code for run {run.id}'):
                sources_blob_keys[run] = run.upload_sources()

        with cli.spinner(f'Upload "{dataset.stem}"') as s:
            result = run.load_result(dataset)
            if not result:
                s.skip()
                continue
            sub = result.submit(sources_blob_keys[run])
            submissions[sub.id] = sub
            results[sub.id] = {
                'result': result,
                'submission': sub,
            }

    scored = {}

    label = 'Wait for remote score calculation ({} to go)'

    best_scores = {}

    with cli.spinner(label.format(len(submissions))) as s:
        while submissions:
            for submission in round.submissions():
                if not submission.scored:
                    continue
                if submission.best:
                    best_scores[submission.data_set.id] = submission.score
                try:
                    del submissions[submission.id]
                    scored[submission.id] = submission
                except KeyError:
                    continue
            s.text = label.format(len(submissions))
            if submissions:
                time.sleep(1)

    # Match submissions to local datasets
    for submission in scored.values():
        results[submission.id]['submission'] = submission

    click.echo()
    best_total_score = sum(best_scores.values(), 0)
    total_score = 0

    for res_sub in results.values():
        result, submission = res_sub['result'], res_sub['submission']

        total_score += submission.score

        if not submission.valid:
            score = click.style('invalid', fg='red')
        elif submission.best:
            score = click.style(f'{submission.score} (best score)', fg='green')
        else:
            score = f'{submission.score}'

        click.echo(f'{result.dataset.stem:>20s}: {score}', nl=False)

        if submission.valid and submission.score != result.score:
            click.secho(
                f' (scoring issue: {result.score} != {submission.score})',
                fg='yellow',
            )
        else:
            click.echo()

    if total_score >= best_total_score:
        score = click.style(f'{total_score} best score', fg='green')
    else:
        score = click.style(f'{total_score} / {best_total_score}')

    click.echo(f'{"TOTAL":>20s}: {score}')
    click.echo()


@main.command(name='reset')
@click.pass_obj
def reset_runs(context):
    # Remove all runs
    context.reset_runs()

    # Reset highscores
    context.data['highscores'] = {}
    context.persist_data()


@main.command(name='dashboard-updater')
@click.pass_obj
def dashboard_updater(obj):
    raise NotImplementedError


if __name__ == '__main__':
    main()
