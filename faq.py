messages = {
    "drive-ua": """Ви можете допомогти іншим на BlaBlaCar

Шановні користувачі, 

Останні кілька днів були дуже складними і непередбачуваними для кожного з нас. Сподіваємось, ви та ваші рідні в безпеці.
Ми знаємо, що багато хто з вас хоче допомогти, оскільки єдність завжди була однією із ключових цінностей спільноти BlaBlaCar. Зважаючи на обставини, неважливі поїздки не рекомендовані. Також ми просимо вас стежити за рекомендаціями уряду.

## Заклик до єдності
Якщо вам потрібно їхати та є вільні місця в авто, ви можете запропонувати їх тим, кому це необхідно.
Сервіс BlaBlaCar безкоштовний, а щоб ви могли допомогти іншим, ми вжили певних заходів  ви можете вказати мінімальну ціну за поїздку.

## Покажіть ваш статус волонтера, щоб запропонувати безкоштовні поїздки
Якщо ви хочете допомогти більше, ви можете запропонувати безкоштовну поїздку, додавши до свого імені слово “Волонтер”, наприклад, “Андрій Бойко (Волонтер). Це допоможе людям швидше вас знайти.

Сьогодні це не наш звичний заклик поділитися своїм автомобілем. Це заклик до єдності та піклування про власну безпеку та безпеку інших.

Наші думки з вами, 
Команда BlaBlaCar""",
    "drive-en": """You can help others with BlaBlaCar

Dear members,
The last few days have been very difficult and unpredictable for each of us. We hope you and your loved ones are safe.
We know that many of you want to help, as solidarity has always been the key value for the BlaBlaCar community. Considering the circumstances, traveling for non-urgent matters is not recommended and we encourage you to check on government recommendations.

## Call for solidarity 
If you have to travel and have free seats in the car, you may want to offer them to others in need.
BlaBlaCar is free of charge, and to help you help others, we have brought changes so that you can now set the lowest minimum price for a trip. 

## Show your volunteer status to offer free trips
If you want to go further, you can also choose to offer a trip for free by adding to your name in your BlaBlaCar profile the mention “(Volunteer)”. For example:  “Andrii Boiko (Volunteer)”. This will help people in need of help to find your free offer more easily. 

Today it is not our usual call to carpool. It is a call for solidarity, a call to take care of your safety and that of others.

Our thoughts are with you,
The BlaBlaCar team""",
}


def faq(topic: str) -> str:
    return messages.get(topic, "Нет такой страницы FAQ")