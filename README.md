# Ansible Collection - apatard.suma

This is a collection mainly providing Ansible Modules for suse manager.
These modules were written alongside the two provided playbooks in order
to automatically register a system to suse manager and delete it from
vagrant.

## Modules

| Module                     | Description                                    |
|----------------------------|------------------------------------------------|
| apatard.suma.saltkey       | Accepts/Deletes/Rejects suse manager salt keys |
| apatard.suma.system_delete | Delete synchronously a system                  |
| apatard.suma.system_info   | Return info about a system registered to SUMA  |
| apatard.suma.systems_facts | Returns all registered systems ids             |

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
- name: Boostrap hosts
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
