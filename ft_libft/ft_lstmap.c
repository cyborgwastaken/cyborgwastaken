/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_lstmap.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: gcyril <marvin@42.fr>                      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2019/11/09 15:53:15 by gcyril            #+#    #+#             */
/*   Updated: 2019/11/09 19:17:48 by gcyril           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

t_list	*ft_lstmap(t_list *lst, void *(*f)(void *), void (*del)(void *))
{
	t_list	*n;
	t_list	*b;

	if (!lst || !*f || !del)
		return (NULL);
	b = NULL;
	while (lst)
	{
		if (!(n = ft_lstnew(f(lst->content))))
		{
			ft_lstclear(&b, del);
			return (NULL);
		}
		ft_lstadd_back(&b, n);
		lst = lst->next;
	}
	return (b);
}
