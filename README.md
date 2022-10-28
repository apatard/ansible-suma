# Ansible Collection - apatard.suma

This is a collection mainly providing Ansible Modules for suse manager.
These modules were written alongside the two provided playbooks in order
to automatically register a system to suse manager and delete it from
vagrant.

## Modules

| Module                     | Description                                    |
|----------------------------|------------------------------------------------|
| apatard.suma.saltkey       | Accepts/Deletes/Rejects suse manager salt keys |
| apatard.suma.system_addon  | Add or remove addons                           |
| apatard.suma.system_delete | Delete synchronously a system                  |
| apatard.suma.system_info   | Return info about a system registered to SUMA  |
| apatard.suma.systems_facts | Returns all registered systems ids             |

## Bootstrap Playbook

This playbook will automatically bootstrap systems on SUSE Manager. It's inspired by what's done by SUSE Manager when bootstrapping.

It will run on the hosts belonging to the ``suma`` group and not on ``all`` systems of the inventory.

Several variables are used:

-  ``suma_rootca``: List of CA certificates to add to the systems
-  ``suma_host``: FQDN of the SUSE Manager instance **Required**
-  ``suma_minion_conf_template``: Template for the first salt minion configuration file. Used only after installing the salt-minion package. Otherwise ansible will overwrite the configuration done later by salt. There's a default template provided with the playbook.
-  ``suma_actkey``: Activation key to use **Required**
-  ``suma_login``: Account on SUSE Manager to use **Required**
-  ``suma_password``: Password for the SUSE Manager account **Required**
-  ``suma_accept_key``: Automatically accept the salt key in SUSE Manager. Defaults to automatically accept.
-  ``suma_host_key``: String to use as minion salt key name. If not specified use the FQDN of the system.
-  ``suma_net_regexp``: Regular expression used to find the IPv4 of the system on the SUSE Manager network. *Required if ``suma_accept_key`` is True or not specified.*


## Delete Playbook

This playbook will unregister a system on SUSE Manager by its ``hostname`` in SUSE Manager. Obviously, if the system host id is known, this playbook can be replaced by a call to ``apatard.suma.system_delete``.


Playbook variables:

-  ``suma_host``: FQDN of the SUSE Manager instance **Required**
-  ``suma_login``: Account on SUSE Manager to use **Required**
-  ``suma_password``: Password for the SUSE Manager account **Required**
-  ``suma_system_name``: Hostname of the system to delete. **Required**


## Example of usage

```
Vagrant.configure("2") do |c|
  c.vm.define 'myvm' do |v|
    v.vm.hostname = 'myvm.example.com'
    v.vm.box = 'sles15sp3'
    v.vm.provider :libvirt do |lv|
      lv.boot 'hd'
      lv.loader = "/usr/share/OVMF/OVMF_CODE.fd"
      lv.memory = 1024
    end
    v.vm.provision :ansible do |ansible|
      ansible.playbook = "playbook.yml"
      ansible.groups = {
        "suma" => [
          "myvm.example.com"
        ],
      }
    end
    v.trigger.before :destroy do |trigger|
      trigger.info = "Unregistering to suma..."
      trigger.run = {inline: "ansible-playbook -i .vagrant/provisioners/ansible/inventory/vagrant_ansible_inventory -e suma_system_name=myvm.example.com delete_playbook.yml" }
    end
  end
end
```

The playbooks are looking like:

```
---
- name: Bootstrap hosts
  import_playbook: apatard.suma.bootstrap
  vars:
    suma_net_regexp: '192\.168\.254.*'
    suma_rootca:
      - src: /path/to/ca.crt
        dest: ca.pem
      - src: /path/to/inter-ca.crt
        dest: inter-ca.crt
    suma_host: suma.example.com
    suma_login: "admin"
    suma_password: "password"
    suma_actkey: "1-mykey"
```

```

---
- name: Unregister system
  import_playbook: apatard.suma.delete
  vars:
    suma_net_regexp: '192\.168\.254.*'
    suma_rootca:
      - src: /path/to/ca.crt
        dest: ca.pem
      - src: /path/to/inter-ca.crt
        dest: inter-ca.crt
    suma_host: suma.example.com
    suma_login: "admin"
    suma_password: "password"
    suma_actkey: "1-mykey"
```
