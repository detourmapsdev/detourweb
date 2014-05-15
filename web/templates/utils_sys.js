/**
 * User: Juan Manuel Ticona Pacheco
 * Date: 10/09/12
 * Time: 02:40 PM
 */

var varDetourmaps={
    {% if user.is_authenticated %}
    user:{
        username:'{{user.username}}',
        login: {{'true'}}
    }
    {% else %}
    user:{
        username:null,
        login: {{'false'}}
    }
    {% endif %}
};

window['varDetourmaps'] = varDetourmaps;