import pytest


def test_roles_exc_not_persisted(organization_factory):
    with pytest.raises(RuntimeError) as exc:
        organization_factory('test-org', roles=['test-org.admin_role:user1'], persisted=False)
    assert 'persisted=False' in str(exc.value)


@pytest.mark.django_db
def test_roles_exc_bad_object(organization_factory):
    with pytest.raises(KeyError):
        organization_factory('test-org', roles=['test-project.admin_role:user'])


@pytest.mark.django_db
def test_roles_exc_not_unique(organization_factory):
    with pytest.raises(KeyError) as exc:
        organization_factory('test-org', projects=['foo'], teams=['foo'], roles=['foo.admin_role:user'])
    assert 'must be unique' in str(exc.value)


@pytest.mark.django_db
def test_roles_exc_not_assignment(organization_factory):
    with pytest.raises(RuntimeError) as exc:
        organization_factory('test-org', projects=['foo'], roles=['foo.admin_role'])
    assert 'provide an assignment' in str(exc.value)


@pytest.mark.django_db
def test_roles_exc_not_found(organization_factory):
    with pytest.raises(RuntimeError) as exc:
        organization_factory('test-org', users=['user'], projects=['foo'], roles=['foo.admin_role:user.bad_role'])
    assert 'unable to find' in str(exc.value)


@pytest.mark.django_db
def test_roles_exc_not_user(organization_factory):
    with pytest.raises(RuntimeError) as exc:
        organization_factory('test-org', projects=['foo'], roles=['foo.admin_role:foo'])
    assert 'unable to add non-user' in str(exc.value)


@pytest.mark.django_db
def test_org_factory_roles(organization_factory):
    objects = organization_factory('org_roles_test',
                                   teams=['team1', 'team2'],
                                   users=['team1:foo', 'bar'],
                                   projects=['baz', 'bang'],
                                   roles=['team2.member_role:foo',
                                          'team2.admin_role:bar',
                                          'team1.admin_role:team2.admin_role',
                                          'baz.admin_role:foo'])

    assert objects.users.bar in objects.teams.team1.admin_role
    assert objects.users.foo in objects.projects.baz.admin_role
    assert objects.users.foo in objects.teams.team1.member_role
    assert objects.teams.team2.admin_role in objects.teams.team1.admin_role.parents.all()


@pytest.mark.django_db
def test_org_factory(organization_factory):
    objects = organization_factory('organization1',
                                   teams=['team1'],
                                   superusers=['superuser'],
                                   users=['admin', 'alice', 'team1:bob'],
                                   projects=['proj1'])
    assert hasattr(objects.users, 'admin')
    assert hasattr(objects.users, 'alice')
    assert hasattr(objects.superusers, 'superuser')
    assert objects.users.bob in objects.teams.team1.member_role.members.all()
    assert objects.projects.proj1.organization == objects.organization


@pytest.mark.django_db
def test_job_template_factory(job_template_factory):
    jt_objects = job_template_factory('testJT', organization='org1',
                                      project='proj1', inventory='inventory1',
                                      credential='cred1')
    assert jt_objects.job_template.name == 'testJT'
    assert jt_objects.project.name == 'proj1'
    assert jt_objects.inventory.name == 'inventory1'
    assert jt_objects.credential.name == 'cred1'
    assert jt_objects.inventory.organization.name == 'org1'
