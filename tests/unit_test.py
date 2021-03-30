import hashlib
import os
from unittest import mock
from unittest.mock import patch

import pybase64
import requests

from blaise_nisra_case_mover import (
    check_if_matching_file_in_bucket,
    check_instrument_database_file_exists,
    get_actual_instrument_database_file_name,
    get_instrument_files,
    get_instrument_folders,
    process_instrument,
    send_request_to_api,
    upload_instrument,
)
from google_storage import GoogleStorage


def test_get_instrument_folders(mock_sftp, sftp_config, config):
    mock_sftp.listdir.return_value = ["OPN2101A", "LMS2101A", "foobar"]
    assert get_instrument_folders(mock_sftp, sftp_config, config) == [
        "OPN2101A",
        "LMS2101A",
    ]


def test_get_instrument_files(mock_sftp, config):
    mock_sftp.listdir.return_value = [
        "oPn2101A.BdBx",
        "oPn2101A.BdIx",
        "oPn2101A.BmIx",
        "oPn2101A.pdf",
        "FrameSOC.blix",
    ]
    assert get_instrument_files(mock_sftp, "", config) == [
        "oPn2101A.BdBx",
        "oPn2101A.BdIx",
        "oPn2101A.BmIx",
        "FrameSOC.blix",
    ]


def test_check_instrument_database_file_exists_returns_false_if_file_list_is_empty():
    file_list = []
    instrument_name = "OPN2101A"
    assert check_instrument_database_file_exists(file_list, instrument_name) is False


def test_check_instrument_database_file_exists_returns_false_if_no_instrument_database_file_found():
    file_list = ["OPN2101A.bdix", "OPN2101A.bmix", "FrameSOC.blix"]
    instrument_name = "OPN2101A"
    assert check_instrument_database_file_exists(file_list, instrument_name) is False


def test_check_instrument_database_file_exists_returns_false_if_different_database_file_found():
    file_list = ["LMS2101A.bdbx", "LMS2101A.bdix", "LMS2101A.bmix", "FrameSOC.blix"]
    instrument_name = "OPN2101A"
    assert check_instrument_database_file_exists(file_list, instrument_name) is False


def test_check_instrument_database_file_exists_returns_true_if_correct_instrument_database_file_found():
    file_list = ["oPn2101A.bDbX", "OPN2101A.bdix", "OPN2101A.bmix", "FrameSOC.blix"]
    instrument_name = "OPN2101A"
    assert check_instrument_database_file_exists(file_list, instrument_name) is True


def test_get_actual_instrument_database_file_name_returns_actual_instrument_database_file_name():
    file_list = ["oPn2101A.bDbX", "OPN2101A.bdix", "OPN2101A.bmix", "FrameSOC.blix"]
    instrument_name = "OPN2101A"
    assert (
        get_actual_instrument_database_file_name(file_list, instrument_name)
        == "oPn2101A.bDbX"
    )


@patch.object(GoogleStorage, "get_blob", return_value=None)
def test_check_if_matching_file_in_bucket_returns_false_if_no_files_in_bucket(
    _mock_get_blob, google_storage
):
    assert (
        check_if_matching_file_in_bucket(
            google_storage, "oPn2101A.bDbX", "OPN2101A/OPN2101A.bdbx"
        )
        is False
    )


@patch.object(GoogleStorage, "get_blob")
@patch.object(hashlib, "md5")
@patch("builtins.open")
def test_check_if_matching_file_in_bucket_returns_true_if_files_match(
    _mock_open, mock_hashlib, mock_get_blob, google_storage
):
    mock_md5 = mock.MagicMock()
    mock_md5.digest.return_value = b"123456789"
    mock_hashlib.return_value = mock_md5
    mock_get_blob.return_value = mock.MagicMock(
        md5_hash=pybase64.b64encode(b"123456789"), name="OPN2101A"
    )
    assert (
        check_if_matching_file_in_bucket(
            google_storage, "oPn2101A.bDbX", "OPN2101A/OPN2101A.bdbx"
        )
        is True
    )


@patch.object(GoogleStorage, "get_blob")
@patch.object(hashlib, "md5")
@patch("builtins.open")
def test_check_if_matching_file_in_bucket_returns_false_if_files_do_not_match(
    _mock_open, mock_hashlib, mock_get_blob, google_storage
):
    mock_md5 = mock.MagicMock()
    mock_md5.digest.return_value = "987654321"
    mock_hashlib.return_value = mock_md5
    mock_get_blob.return_value = mock.MagicMock(
        md5_hash=pybase64.b64encode(b"123456789"), name="OPN2101A"
    )
    assert (
        check_if_matching_file_in_bucket(
            google_storage, "oPn2101A.bDbX", "OPN2101A/OPN2101A.bdbx"
        )
        is False
    )


@patch("blaise_nisra_case_mover.delete_local_instrument_files")
@patch("blaise_nisra_case_mover.get_instrument_files")
@patch("blaise_nisra_case_mover.check_instrument_database_file_exists")
@patch("blaise_nisra_case_mover.get_actual_instrument_database_file_name")
@patch("blaise_nisra_case_mover.check_if_matching_file_in_bucket")
@patch("blaise_nisra_case_mover.upload_instrument")
@patch("blaise_nisra_case_mover.send_request_to_api")
def test_process_instrument_if_no_instrument_files(
    mock_send_request_to_api,
    mock_upload_instrument,
    mock_check_if_matching_file_in_bucket,
    mock_get_actual_instrument_database_file_name,
    mock_check_instrument_database_file_exists,
    mock_get_instrument_files,
    mock_delete_local_instrument_files,
    mock_sftp,
    google_storage,
    config,
):
    mock_send_request_to_api.assert_not_called()
    mock_get_instrument_files.return_value = []
    assert (
        process_instrument(mock_sftp, google_storage, "ONS/OPN/OPN2101A/", config)
        == "No instrument files found in folder - ONS/OPN/OPN2101A/"
    )
    mock_delete_local_instrument_files.assert_called_once()
    mock_get_actual_instrument_database_file_name.assert_not_called()
    mock_check_instrument_database_file_exists.assert_not_called()
    mock_check_if_matching_file_in_bucket.assert_not_called()
    mock_upload_instrument.assert_not_called()


@patch("blaise_nisra_case_mover.delete_local_instrument_files")
@patch("blaise_nisra_case_mover.get_instrument_files")
@patch("blaise_nisra_case_mover.check_instrument_database_file_exists")
@patch("blaise_nisra_case_mover.get_actual_instrument_database_file_name")
@patch("blaise_nisra_case_mover.check_if_matching_file_in_bucket")
@patch("blaise_nisra_case_mover.upload_instrument")
@patch("blaise_nisra_case_mover.send_request_to_api")
def test_process_instrument_if_no_instrument_database_file(
    mock_send_request_to_api,
    mock_upload_instrument,
    mock_check_if_matching_file_in_bucket,
    mock_get_actual_instrument_database_file_name,
    mock_check_instrument_database_file_exists,
    mock_get_instrument_files,
    mock_delete_local_instrument_files,
    mock_sftp,
    google_storage,
    config,
):
    mock_send_request_to_api.assert_not_called()
    mock_upload_instrument.assert_not_called()
    mock_check_if_matching_file_in_bucket.assert_not_called()
    mock_get_actual_instrument_database_file_name.assert_not_called()
    mock_check_instrument_database_file_exists.return_value = False
    mock_get_instrument_files.return_value = [
        "OPN2101A.bdix",
        "OPN2101A.bmix",
        "FrameSOC.blix",
        "foobar.bdbx",
    ]
    assert (
        process_instrument(mock_sftp, google_storage, "ONS/OPN/OPN2101A/", config)
        == "Instrument database file not found - OPN2101A.bdbx"
    )
    mock_delete_local_instrument_files.assert_called_once()


@patch("blaise_nisra_case_mover.delete_local_instrument_files")
@patch("blaise_nisra_case_mover.get_instrument_files")
@patch("blaise_nisra_case_mover.check_instrument_database_file_exists")
@patch("blaise_nisra_case_mover.get_actual_instrument_database_file_name")
@patch("blaise_nisra_case_mover.check_if_matching_file_in_bucket")
@patch("blaise_nisra_case_mover.upload_instrument")
@patch("blaise_nisra_case_mover.send_request_to_api")
def test_process_instrument_uploads_instrument_if_database_files_do_not_match(
    mock_send_request_to_api,
    mock_upload_instrument,
    mock_check_if_matching_file_in_bucket,
    mock_get_actual_instrument_database_file_name,
    mock_check_instrument_database_file_exists,
    mock_get_instrument_files,
    mock_delete_local_instrument_files,
    mock_sftp,
    google_storage,
    config,
):
    mock_check_if_matching_file_in_bucket.return_value = False
    mock_get_actual_instrument_database_file_name.return_value = "oPN2101A.bDbx"
    mock_check_instrument_database_file_exists.return_value = True
    mock_get_instrument_files.return_value = [
        "OPN2101A.bDix",
        "OPN2101A.bmix",
        "OPN2101A.blix",
        "oPN2101A.bDbx",
    ]
    process_instrument(mock_sftp, google_storage, "ONS/OPN/OPN2101A/", config)
    mock_send_request_to_api.assert_called_once_with("OPN2101A")
    mock_upload_instrument.assert_called_once_with(
        mock_sftp,
        google_storage,
        "ONS/OPN/OPN2101A/",
        "OPN2101A",
        ["OPN2101A.bDix", "OPN2101A.bmix", "OPN2101A.blix", "oPN2101A.bDbx"],
    )
    mock_delete_local_instrument_files.assert_called_once()


@patch("blaise_nisra_case_mover.delete_local_instrument_files")
@patch("blaise_nisra_case_mover.get_instrument_files")
@patch("blaise_nisra_case_mover.check_instrument_database_file_exists")
@patch("blaise_nisra_case_mover.get_actual_instrument_database_file_name")
@patch("blaise_nisra_case_mover.check_if_matching_file_in_bucket")
@patch("blaise_nisra_case_mover.upload_instrument")
@patch("blaise_nisra_case_mover.send_request_to_api")
def test_process_instrument_doesnt_upload_instrument_if_database_files_do_match(
    mock_send_request_to_api,
    mock_upload_instrument,
    mock_check_if_matching_file_in_bucket,
    mock_get_actual_instrument_database_file_name,
    mock_check_instrument_database_file_exists,
    mock_get_instrument_files,
    mock_delete_local_instrument_files,
    mock_sftp,
    google_storage,
    config,
):
    mock_send_request_to_api.assert_not_called()
    mock_check_instrument_database_file_exists.return_value = True
    mock_get_actual_instrument_database_file_name.return_value = "OPN2101A.bdbx"
    mock_check_if_matching_file_in_bucket.return_value = True
    process_instrument(mock_sftp, google_storage, "ONS/OPN/OPN2101A/", config)
    mock_upload_instrument.assert_not_called()
    mock_get_instrument_files.assert_called_once()
    mock_delete_local_instrument_files.assert_called_once()


@patch.object(GoogleStorage, "upload_file")
def test_upload_instrument(mock_google_storage, mock_sftp, google_storage):
    instrument_name = "OPN2101A"
    instrument_files = [
        "OPN2101A.bDix",
        "OPN2101A.bmix",
        "OPN2101A.blix",
        "OPN2101A.bdbx",
    ]
    upload_instrument(
        mock_sftp,
        google_storage,
        "ONS/OPN/OPN2101A/",
        instrument_name,
        instrument_files,
    )
    assert mock_google_storage.call_count == len(instrument_files)
    for instrument_file in instrument_files:
        mock_google_storage.assert_any_call(
            instrument_file, f"{instrument_name}/{instrument_file}".upper()
        )


@mock.patch.dict(os.environ, {"BLAISE_API_URL": "MOCK_BLAISE_API_URL"})
@mock.patch.dict(os.environ, {"SERVER_PARK": "MOCK_SERVER_PARK"})
@patch.object(requests, "post")
def test_send_request_to_api(mock_requests_post, config):
    send_request_to_api("OPN2101A", config)
    mock_requests_post.assert_called_once_with(
        "http://MOCK_BLAISE_API_URL/api/v1/serverparks/MOCK_SERVER_PARK/instruments/OPN2101A/data",
        data='{"instrumentDataPath": "OPN2101A"}',
        headers={"content-type": "application/json"},
        timeout=10,
    )
