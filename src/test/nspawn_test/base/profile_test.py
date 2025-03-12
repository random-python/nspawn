from nspawn.base.profile import *


def verify_entry(origin:AnyEntry, entry_token:str, option_token:str) -> None:
    render_entry = origin.render_entry()
    render_option = origin.render_option()
    print(f"{origin} :: {render_entry} :: {render_option}")
    assert render_entry == entry_token
    assert render_option == option_token
    parsed_entry = parse_profile_entry(render_entry)
    assert origin == parsed_entry
    if option_token:
        parsed_option = parse_profile_option(option_token)
        assert origin == parsed_option


def test_profile_entry():
    print()

    print("### special")
    verify_entry(ProfileEntry.Quiet("no"), "Quiet=no", None)
    verify_entry(ProfileEntry.Quiet("yes"), "Quiet=yes", "--quiet")
    verify_entry(ProfileEntry.KeepUnit("no"), "KeepUnit=no", None)
    verify_entry(ProfileEntry.KeepUnit("yes"), "KeepUnit=yes", "--keep-unit")
    verify_entry(ProfileEntry.Register("no"), "Register=no", "--register=no")
    verify_entry(ProfileEntry.Register("yes"), "Register=yes", "--register=yes")
    verify_entry(ProfileEntry.Property("key=val"), "Property=key=val", "--property=key=val")
    verify_entry(ProfileEntry.Slice("system"), "Slice=system", "--slice=system")

    print("### [Exec]")
    verify_entry(ProfileEntry.Boot("no"), "Boot=no", None)
    verify_entry(ProfileEntry.Boot("yes"), "Boot=yes", "--boot")
    verify_entry(ProfileEntry.Ephemeral("no"), "Ephemeral=no", None)
    verify_entry(ProfileEntry.Ephemeral("yes"), "Ephemeral=yes", "--ephemeral")
    verify_entry(ProfileEntry.ProcessTwo("no"), "ProcessTwo=no", None)
    verify_entry(ProfileEntry.ProcessTwo("yes"), "ProcessTwo=yes", "--as-pid2")

    verify_entry(ProfileEntry.Environment("KEY=VAL"), "Environment=KEY=VAL", "--setenv=KEY=VAL")
    verify_entry(ProfileEntry.User("user0"), "User=user0", "--user=user0")
    verify_entry(ProfileEntry.WorkingDirectory("/root"), "WorkingDirectory=/root", "--chdir=/root")

    print("### [Files]")
    verify_entry(ProfileEntry.Bind("/path1:/path2"), "Bind=/path1:/path2", "--bind=/path1:/path2")
    verify_entry(ProfileEntry.BindReadOnly("/path1:/path2"), "BindReadOnly=/path1:/path2", "--bind-ro=/path1:/path2")

    print("### [Network]")
    verify_entry(ProfileEntry.MACVLAN("eth0"), "MACVLAN=eth0", "--network-macvlan=eth0")
    verify_entry(ProfileEntry.Port("tcp:10101:20202"), "Port=tcp:10101:20202", "--port=tcp:10101:20202")


def test_profile_entry_list():
    print()
    entry_list = profile_entry_list()
    print(entry_list)
    assert len(entry_list) == 49


def test_profile_option_list():
    print()
    option_list = profile_option_list()
    print(option_list)
    assert len(option_list) == 49


def test_profile_option_mapper():
    print()
    mapper = profile_option_mapper()
    print(mapper)
    assert len(mapper) == 49


def test_profile_one():
    print()
    bucket = ProfileBucket()
    bucket.with_append_entry('Boot', 'yes')
    bucket.with_append_entry('Bind', '/root:/root')
    print(bucket)
    entry_list = bucket.render_entry_list()
    option_list = bucket.render_option_list()
    print(entry_list)
    print(option_list)
    assert bucket.command == None
    assert entry_list == ['Boot=yes', 'Bind=/root:/root']
    assert option_list == ['--boot', '--bind=/root:/root']


def test_profile_two():
    print()
    bucket = ProfileBucket()
    bucket.with_command(['/bin/init', '--root'])
    bucket.with_append_entry('Boot', 'no')
    bucket.with_append_entry('Bind', '/root:/root')
    print(bucket)
    entry_list = bucket.render_entry_list()
    option_list = bucket.render_option_list()
    print(entry_list)
    print(option_list)
    assert bucket.command == ['/bin/init', '--root']
    assert entry_list == ['Boot=no', 'Bind=/root:/root']
    assert option_list == ['--bind=/root:/root']


def test_selected_list():
    print()
    version = 235
    class_list = list(profile_option_mapper().values())
    total_list = list(map(lambda class_name: class_name(''), class_list))
    supported_list = supported_entry_list(version, total_list)
    unsupported_list = unsupported_entry_list(version, total_list)
    print(total_list)
    print(supported_list)
    print(unsupported_list)
    assert len(total_list) == 49
    assert len(supported_list) == 39
    assert len(unsupported_list) == 10


def test_partition_bucket():
    print()
    version = 235
    token_list = [
        '--bind=/root',
        '--hostname=image',
    ]
    bucket = PartitionBucket.parse_option_list(version, token_list)
    supported_list = bucket.supported_list()
    unsupported_list = bucket.unsupported_list()
    print(bucket)
    print(supported_list)
    print(unsupported_list)
    assert bucket.has_supported()
    assert bucket.has_unsupported()
    assert supported_list == [ProfileEntry.Bind('/root')]
    assert unsupported_list == [ProfileEntry.Hostname('image')]
