import io
from datetime import datetime
from unittest import mock

from models.instruments import Instrument
from sftp import SFTP


def test_get_instrument_folders(mock_sftp_connection, sftp_config, config):
    mock_sftp_connection.listdir.return_value = [
        "OPN2101A",
        "LMS2101A",
        "lMS2101A",
        "lMS2101a",
        "foobar",
    ]
    sftp = SFTP(mock_sftp_connection, sftp_config, config)
    assert sftp.get_instrument_folders() == {
        "OPN2101A": Instrument(sftp_path="./ONS/OPN/OPN2101A"),
        "LMS2101A": Instrument(sftp_path="./ONS/OPN/LMS2101A"),
        "lMS2101A": Instrument(sftp_path="./ONS/OPN/lMS2101A"),
        "lMS2101a": Instrument(sftp_path="./ONS/OPN/lMS2101a"),
    }


def test_get_instrument_files(
    mock_sftp_connection, sftp_config, config, mock_list_dir_attr
):
    sftp = SFTP(mock_sftp_connection, sftp_config, config)
    instrument_folders = {"OPN2101A": Instrument(sftp_path="ONS/OPN/OPN2101A")}
    mock_sftp_connection.listdir_attr.return_value = [
        mock_list_dir_attr(filename="oPn2101A.BdBx", st_mtime=1617186113),
        mock_list_dir_attr(filename="oPn2101A.BdIx", st_mtime=1617186091),
        mock_list_dir_attr(filename="oPn2101A.BmIx", st_mtime=1617186113),
        mock_list_dir_attr(filename="oPn2101A.pdf", st_mtime=1617186117),
        mock_list_dir_attr(filename="FrameSOC.blix", st_mtime=1617186117),
    ]

    assert sftp.get_instrument_files(instrument_folders) == {
        "OPN2101A": Instrument(
            sftp_path="ONS/OPN/OPN2101A",
            bdbx_updated_at=datetime.fromisoformat("2021-03-31T10:21:53+00:00"),
            files=[
                "oPn2101A.BdBx",
                "oPn2101A.BdIx",
                "oPn2101A.BmIx",
                "FrameSOC.blix",
            ],
        )
    }


def test_filter_instrument_files_removes_instruments_without_bdbx_files(
    mock_sftp_connection, sftp_config, config
):
    instrument_folders = {
        "OPN2101A": Instrument(
            sftp_path="ONS/OPN/OPN2101A",
            bdbx_updated_at=datetime.fromisoformat("2021-03-31T10:21:53+00:00"),
            files=[
                "oPn2101A.BdBx",
                "oPn2101A.BdIx",
                "oPn2101A.BmIx",
                "FrameSOC.blix",
            ],
        ),
        "OPN2102A": Instrument(
            sftp_path="ONS/OPN/OPN2102A",
            bdbx_updated_at=datetime.fromisoformat("2021-03-31T10:21:53+00:00"),
            files=[
                "oPn2102A.BdIx",
                "oPn2102A.BmIx",
                "FrameSOC.blix",
            ],
        ),
        "OPN2103A": Instrument(
            sftp_path="ONS/OPN/OPN2103A",
            bdbx_updated_at=datetime.fromisoformat("2021-03-31T10:21:53+00:00"),
            files=[
                "oPn2103A.BdBx",
            ],
        ),
    }
    sftp = SFTP(mock_sftp_connection, sftp_config, config)
    assert sftp.filter_instrument_files(instrument_folders) == {
        "OPN2101A": Instrument(
            sftp_path="ONS/OPN/OPN2101A",
            bdbx_updated_at=datetime.fromisoformat("2021-03-31T10:21:53+00:00"),
            files=[
                "oPn2101A.BdBx",
                "oPn2101A.BdIx",
                "oPn2101A.BmIx",
                "FrameSOC.blix",
            ],
        ),
        "OPN2103A": Instrument(
            sftp_path="ONS/OPN/OPN2103A",
            bdbx_updated_at=datetime.fromisoformat("2021-03-31T10:21:53+00:00"),
            files=[
                "oPn2103A.BdBx",
            ],
        ),
    }


def test_filter_instrument_files_returns_the_latest_modified_when_names_clash(
    mock_sftp_connection, sftp_config, config
):
    instrument_folders = {
        "OPN2101A": Instrument(
            sftp_path="ONS/OPN/OPN2101A",
            bdbx_updated_at=datetime.fromisoformat("2021-03-31T10:21:53+00:00"),
            files=[
                "oPn2101A.BdBx",
                "oPn2101A.BdIx",
                "oPn2101A.BmIx",
                "FrameSOC.blix",
            ],
        ),
        "oPN2101A": Instrument(
            sftp_path="ONS/OPN/oPN2101A",
            bdbx_updated_at=datetime.fromisoformat("2021-04-30T10:21:53+00:00"),
            files=[
                "oPn2101A.BdBx",
                "oPn2101A.BdIx",
                "oPn2101A.BmIx",
                "FrameSOC.blix",
            ],
        ),
        "OpN2101A": Instrument(
            sftp_path="ONS/OPN/OpN2101A",
            bdbx_updated_at=datetime.fromisoformat("2021-03-31T11:21:53+00:00"),
            files=[
                "oPn2101A.BdBx",
                "oPn2101A.BdIx",
                "oPn2101A.BmIx",
                "FrameSOC.blix",
            ],
        ),
        "OPN2103A": Instrument(
            sftp_path="ONS/OPN/OPN2103A",
            bdbx_updated_at=datetime.fromisoformat("2021-05-20T10:21:53+00:00"),
            files=[
                "oPn2103A.BdBx",
            ],
        ),
    }
    sftp = SFTP(mock_sftp_connection, sftp_config, config)
    assert sftp.filter_instrument_files(instrument_folders) == {
        "opn2101a": Instrument(
            sftp_path="ONS/OPN/oPN2101A",
            bdbx_updated_at=datetime.fromisoformat("2021-04-30T10:21:53+00:00"),
            files=[
                "oPn2101A.BdBx",
                "oPn2101A.BdIx",
                "oPn2101A.BmIx",
                "FrameSOC.blix",
            ],
        ),
        "OPN2103A": Instrument(
            sftp_path="ONS/OPN/OPN2103A",
            bdbx_updated_at=datetime.fromisoformat("2021-05-20T10:21:53+00:00"),
            files=[
                "oPn2103A.BdBx",
            ],
        ),
    }


@mock.patch.object(SFTP, "generate_bdbx_md5", return_value="my_lovely_md5")
def test_get_bdbx_md5s(
    mock_generate_bdbx_md5, mock_sftp_connection, sftp_config, config
):
    instruments = {
        "opn2101a": Instrument(
            sftp_path="ONS/OPN/oPN2101A",
            bdbx_updated_at=datetime.fromisoformat("2021-04-30T10:21:53+00:00"),
            files=[
                "oPn2101A.BdBx",
                "oPn2101A.BdIx",
                "oPn2101A.BmIx",
                "FrameSOC.blix",
            ],
        ),
        "OPN2103A": Instrument(
            sftp_path="ONS/OPN/OPN2103A",
            bdbx_updated_at=datetime.fromisoformat("2021-05-20T10:21:53+00:00"),
            files=[
                "oPn2103A.BdBx",
            ],
        ),
    }
    sftp = SFTP(mock_sftp_connection, sftp_config, config)
    assert sftp.generate_bdbx_md5s(instruments) == {
        "opn2101a": Instrument(
            sftp_path="ONS/OPN/oPN2101A",
            bdbx_updated_at=datetime.fromisoformat("2021-04-30T10:21:53+00:00"),
            bdbx_md5="my_lovely_md5",
            files=[
                "oPn2101A.BdBx",
                "oPn2101A.BdIx",
                "oPn2101A.BmIx",
                "FrameSOC.blix",
            ],
        ),
        "OPN2103A": Instrument(
            sftp_path="ONS/OPN/OPN2103A",
            bdbx_updated_at=datetime.fromisoformat("2021-05-20T10:21:53+00:00"),
            bdbx_md5="my_lovely_md5",
            files=[
                "oPn2103A.BdBx",
            ],
        ),
    }
    assert mock_generate_bdbx_md5.call_count == 2


def test_generate_bdbx_md5(mock_sftp_connection, sftp_config, config, mock_stat):
    fake_file = io.BytesIO(b"My fake bdbx file")
    mock_sftp_connection.stat.return_value = mock_stat(st_size=17)
    mock_sftp_connection.open.return_value = fake_file
    instrument = Instrument(
        sftp_path="ONS/OPN/OPN2103A",
        bdbx_updated_at=datetime.fromisoformat("2021-05-20T10:21:53+00:00"),
        bdbx_md5="my_lovely_md5",
        files=[
            "opn2103a.bdbx",
        ],
    )
    sftp = SFTP(mock_sftp_connection, sftp_config, config)
    # The md5 value for the fake file
    assert sftp.generate_bdbx_md5(instrument) == "50cc5a0bbd05754f98022a25566220fe"
    mock_sftp_connection.stat.assert_called_with("ONS/OPN/OPN2103A/opn2103a.bdbx")
